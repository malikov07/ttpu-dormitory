from aiogram.fsm.state import State, StatesGroup


class ApplicationForm(StatesGroup):
    """FSM states for the dormitory application flow."""
    full_name = State()
    sex = State()
    level = State()
    faculty = State()
    region = State()
    town = State()
    town_custom = State()
    reason = State()
    reason_custom = State()
    official_doc = State()
    passport_photo = State()
    photo_3x4 = State()
    phone_number = State()
    additional_phone = State()
    preview = State()
    select_edit_field = State()


class DocumentReupload(StatesGroup):
    """Sending a corrected official document after the application is in.

    Separate from ApplicationForm: the applicant is not editing their
    application — that stays closed — they are handing the tutors one more file.
    """
    collecting = State()
