"""
app.py
PinForge AI — Streamlit dashboard. Entry point: `streamlit run app.py`

Flow: Sign up / log in -> Connect Pinterest (official OAuth2) -> Upload images ->
AI generates pin content -> pick board -> add to safety-scheduled queue ->
background scheduler posts within daily caps + randomized delays -> view history.
"""

import uuid
from datetime import datetime

import streamlit as st

from config import Config
from database import init_db, get_session
from models import User, PinterestAccount, PinQueueItem, PinStatus
from pinterest_api import PinterestAPI, PinterestAPIError
from ai_engine import AIContentGenerator, AIEngineError
from image_processor import ImageProcessor
from scheduler import (
    start_scheduler, enqueue_pin, get_queue_for_account, get_history_for_account,
    pins_posted_today,
)
from utils import (
    ensure_dirs, is_valid_email, validate_image_extension, validate_file_size,
    hash_content, get_logger, hash_password, verify_password,
)

logger = get_logger("app")

st.set_page_config(page_title="PinForge AI", page_icon="📌", layout="wide")
ensure_dirs()
init_db()
start_scheduler()

for warning in Config.validate():
    st.sidebar.warning(warning)

# ---------------- session state ----------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "oauth_state" not in st.session_state:
    st.session_state.oauth_state = uuid.uuid4().hex


# ================= AUTH =================

def auth_screen():
    st.title("📌 PinForge AI")
    st.caption("Safe, official Pinterest API automation — no scraping, no bots.")

    tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in")
        if submitted:
            with get_session() as db:
                user = db.query(User).filter(User.email == email.strip().lower()).first()
                if user and verify_password(password, user.password_hash):
                    st.session_state.user_id = user.id
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

    with tab_signup:
        with st.form("signup_form"):
            email = st.text_input("Email", key="su_email")
            password = st.text_input("Password (min 8 chars)", type="password", key="su_pw")
            confirm = st.text_input("Confirm password", type="password", key="su_pw2")
            submitted = st.form_submit_button("Create account")
        if submitted:
            if not is_valid_email(email):
                st.error("Enter a valid email.")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                with get_session() as db:
                    if db.query(User).filter(User.email == email.strip().lower()).first():
                        st.error("Account already exists with that email.")
                    else:
                        user = User(email=email.strip().lower(), password_hash=hash_password(password))
                        db.add(user)
                        db.flush()
                        st.success("Account created. Please log in.")


# ================= PINTEREST CONNECT =================

def handle_oauth_callback():
    """Pinterest redirects back here with ?code=...&state=... after user approves."""
    params = st.query_params
    code = params.get("code")
    state = params.get("state")
    if not code:
        return
    if state != st.session_state.oauth_state:
        st.error("OAuth state mismatch — please retry connecting Pinterest.")
        return
    try:
        token_data = PinterestAPI.exchange_code_for_token(code)
        api = PinterestAPI(access_token=token_data["access_token"])
        account_info = api.get_user_account()

        with get_session() as db:
            existing = (
                db.query(PinterestAccount)
                .filter(
                    PinterestAccount.user_id == st.session_state.user_id,
                    PinterestAccount.pinterest_user_id == account_info.get("username", "unknown"),
                )
                .first()
            )
            expires_at = datetime.utcnow()
            if existing:
                existing.access_token = token_data["access_token"]
                existing.refresh_token = token_data.get("refresh_token", existing.refresh_token)
            else:
                db.add(
                    PinterestAccount(
                        user_id=st.session_state.user_id,
                        pinterest_user_id=account_info.get("username", "unknown"),
                        username=account_info.get("username"),
                        access_token=token_data["access_token"],
                        refresh_token=token_data.get("refresh_token"),
                        token_expires_at=expires_at,
                    )
                )
        st.success("Pinterest account connected!")
        st.query_params.clear()
        st.rerun()
    except PinterestAPIError as e:
        st.error(f"Pinterest connection failed: {e}")


def connect_pinterest_button():
    auth_url = PinterestAPI.get_authorization_url(state=st.session_state.oauth_state)
    st.link_button("🔗 Connect Pinterest Account", auth_url, type="primary")
    st.caption("You'll be redirected to Pinterest to approve access, then sent back here.")


# ================= MAIN DASHBOARD =================

def get_user_accounts(db, user_id):
    return db.query(PinterestAccount).filter(PinterestAccount.user_id == user_id, PinterestAccount.is_active == True).all()  # noqa: E712


def dashboard():
    st.sidebar.title("📌 PinForge AI")
    st.sidebar.caption(f"Logged in")
    if st.sidebar.button("Log out"):
        st.session_state.user_id = None
        st.rerun()

    with get_session() as db:
        accounts = get_user_accounts(db, st.session_state.user_id)
        account_options = {f"@{a.username or a.pinterest_user_id} (id {a.id})": a.id for a in accounts}

    page = st.sidebar.radio("Navigate", ["Connect Account", "Create & Queue Pins", "Queue", "History & Analytics", "Safety Settings"])

    if not accounts and page != "Connect Account":
        st.warning("Connect a Pinterest account first.")
        connect_pinterest_button()
        return

    if page == "Connect Account":
        st.header("Connect Pinterest")
        if accounts:
            st.success(f"{len(accounts)} account(s) connected.")
            for a in accounts:
                st.write(f"• @{a.username or a.pinterest_user_id} — connected {a.connected_at.strftime('%Y-%m-%d')}")
        connect_pinterest_button()

    elif page == "Create & Queue Pins":
        create_and_queue_page(account_options)

    elif page == "Queue":
        queue_page(account_options)

    elif page == "History & Analytics":
        history_page(account_options)

    elif page == "Safety Settings":
        safety_settings_page()


def create_and_queue_page(account_options):
    st.header("Create & Queue Pins")
    account_label = st.selectbox("Pinterest account", list(account_options.keys()))
    account_id = account_options[account_label]

    with get_session() as db:
        posted_today = pins_posted_today(db, account_id)
    st.info(f"Posted today: {posted_today}/{Config.MAX_PINS_PER_ACCOUNT_PER_DAY} (resets rolling 24h)")

    uploaded_files = st.file_uploader(
        "Upload product image(s)", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True
    )
    product_description = st.text_area("Describe the product/topic (for AI content generation)")
    keywords = st.text_input("Target keywords (optional, comma-separated)")
    destination_link = st.text_input("Destination link (optional — your site/product page)")

    # Board selection
    with get_session() as db:
        account = db.query(PinterestAccount).get(account_id)
    boards, board_error = [], None
    try:
        api = PinterestAPI(access_token=account.access_token)
        boards = api.list_boards()
    except PinterestAPIError as e:
        board_error = str(e)

    board_names = {b["name"]: b["id"] for b in boards} if boards else {}
    col1, col2 = st.columns([2, 1])
    with col1:
        board_choice = st.selectbox("Board", list(board_names.keys()) + ["+ Create new board"]) if board_names else "+ Create new board"
    new_board_name = None
    if board_choice == "+ Create new board":
        with col2:
            new_board_name = st.text_input("New board name")
    if board_error:
        st.caption(f"(Could not load boards: {board_error})")

    if st.button("🤖 Generate AI content & add to queue", type="primary", disabled=not uploaded_files):
        with get_session() as db:
            account = db.query(PinterestAccount).get(account_id)

            # resolve / create board
            board_id = None
            if board_choice == "+ Create new board" and new_board_name:
                try:
                    api = PinterestAPI(access_token=account.access_token)
                    new_board = api.create_board(new_board_name)
                    board_id = new_board["id"]
                except PinterestAPIError as e:
                    st.error(f"Board creation failed: {e}")
                    return
            elif board_choice in board_names:
                board_id = board_names[board_choice]

            if not board_id:
                st.error("Select or create a board first.")
                return

            processor = ImageProcessor()
            generator = AIContentGenerator()

            for f in uploaded_files:
                file_bytes = f.read()
                if not validate_image_extension(f.name) or not validate_file_size(len(file_bytes)):
                    st.error(f"Skipped {f.name}: invalid type or too large.")
                    continue

                processed = processor.process(file_bytes, f.name)

                try:
                    content = generator.generate_pin_content(
                        product_description or f.name, image_bytes=file_bytes, keywords=keywords
                    )
                except AIEngineError as e:
                    st.warning(f"AI generation failed for {f.name}, using fallback text: {e}")
                    content = {
                        "title": (product_description or f.name)[:100],
                        "description": (product_description or "")[:500],
                        "hashtags": "",
                        "alt_text": (product_description or f.name)[:500],
                    }

                content_hash = hash_content(content["title"], content["description"])

                item = enqueue_pin(
                    db,
                    account_id=account_id,
                    image_path=processed["processed_path"],
                    title=content["title"],
                    description=content["description"],
                    alt_text=content["alt_text"],
                    hashtags=content["hashtags"],
                    board_id=board_id,
                    content_hash=processed["content_hash"],
                    destination_link=destination_link or None,
                )
                st.success(f"Queued: \"{item.title}\" → posts ~{item.scheduled_for.strftime('%Y-%m-%d %H:%M UTC')}")
                with st.expander(f"Preview: {f.name}"):
                    st.image(processed["processed_path"], width=200)
                    st.write(f"**Title:** {content['title']}")
                    st.write(f"**Description:** {content['description']}")
                    st.write(f"**Hashtags:** {content['hashtags']}")
                    st.write(f"**Alt text:** {content['alt_text']}")


def queue_page(account_options):
    st.header("Posting Queue")
    account_label = st.selectbox("Pinterest account", list(account_options.keys()), key="queue_acct")
    account_id = account_options[account_label]

    with get_session() as db:
        items = get_queue_for_account(db, account_id)

    if not items:
        st.info("Queue is empty.")
        return

    for item in items:
        status_emoji = {
            PinStatus.QUEUED: "⏳", PinStatus.SCHEDULED: "🕒", PinStatus.POSTED: "✅",
            PinStatus.FAILED: "❌", PinStatus.SKIPPED_DUPLICATE: "♻️", PinStatus.SKIPPED_RATE_LIMIT: "🚦",
        }.get(item.status, "❔")
        with st.container(border=True):
            c1, c2 = st.columns([1, 4])
            with c1:
                st.image(item.image_path, width=120)
            with c2:
                st.write(f"{status_emoji} **{item.title}**  ·  status: `{item.status.value}`")
                st.caption(f"Scheduled: {item.scheduled_for} | Board: {item.board_id}")
                if item.error_message:
                    st.caption(f"⚠️ {item.error_message}")


def history_page(account_options):
    st.header("History & Analytics")
    account_label = st.selectbox("Pinterest account", list(account_options.keys()), key="hist_acct")
    account_id = account_options[account_label]

    with get_session() as db:
        history = get_history_for_account(db, account_id)
        posted_today = pins_posted_today(db, account_id)

    col1, col2, col3 = st.columns(3)
    col1.metric("Posted today", posted_today)
    col2.metric("Daily cap", Config.MAX_PINS_PER_ACCOUNT_PER_DAY)
    total_posted = sum(1 for h in history if h.status == PinStatus.POSTED)
    col3.metric("Total posted (recent log)", total_posted)

    st.subheader("Recent activity")
    for h in history:
        st.write(f"`{h.occurred_at.strftime('%Y-%m-%d %H:%M')}` — **{h.status.value}** — {h.title or ''} — {h.detail or ''}")


def safety_settings_page():
    st.header("Safety Settings (read-only — enforced server-side)")
    st.write(f"**Max pins / account / day:** {Config.MAX_PINS_PER_ACCOUNT_PER_DAY}")
    st.write(f"**Delay between posts:** {Config.MIN_DELAY_MINUTES}–{Config.MAX_DELAY_MINUTES} minutes (randomized)")
    st.write("**Duplicate content:** blocked automatically by content hash per account")
    st.write("**API used:** Official Pinterest API v5 (OAuth2) only — no scraping or automation outside ToS")
    st.caption("To change limits, edit MAX_PINS_PER_ACCOUNT_PER_DAY / MIN_DELAY_MINUTES / MAX_DELAY_MINUTES in your .env. Hard upper bounds are enforced in config.py and cannot be bypassed via the UI.")


# ================= ROUTER =================

if st.session_state.user_id is None:
    auth_screen()
else:
    if "code" in st.query_params:
        handle_oauth_callback()
    dashboard()
