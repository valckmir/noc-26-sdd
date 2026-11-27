from datetime import timedelta

import streamlit as st
from sqlmodel import Session

from cathotel.config import get_settings
from cathotel.database import create_database_engine, create_db_and_tables
from cathotel.services.dates import facility_today
from cathotel.models import REVIEW_MAX_LENGTH, Reservation, ReservationStatus
from cathotel.services.feedback import (
    FeedbackError,
    can_leave_feedback,
    get_feedback,
    submit_feedback,
)
from cathotel.services.reservations import (
    ReservationError,
    check_availability,
    create_reservation,
    get_reservation,
    cancel_reservation,
    validate_stay_dates,
)


def _get_engine():
    settings = get_settings()
    engine = create_database_engine(settings.database_path)
    create_db_and_tables(engine)
    return settings, engine


def main() -> None:
    st.set_page_config(page_title="CatHotel", page_icon="🐈")
    st.title("CatHotel")
    page = st.radio("Customer actions", ["Book a stay", "Manage reservation"], horizontal=True)
    if page == "Manage reservation":
        manage_reservation()
        return
    st.header("Book a stay for your cat")
    st.write("Choose your dates to check room availability.")

    try:
        settings, engine = _get_engine()
        today = facility_today(settings.hotel_timezone)
    except Exception as error:
        st.error(f"The booking service is not configured: {error}")
        return

    arrival_date = st.date_input(
        "Arrival date",
        value=today,
        min_value=today,
        key="arrival_date",
    )
    departure_date = st.date_input(
        "Departure date",
        value=today + timedelta(days=1),
        min_value=today + timedelta(days=1),
        key="departure_date",
    )
    check = st.button("Check availability")

    if check:
        try:
            validate_stay_dates(
                arrival_date,
                departure_date,
                hotel_timezone=settings.hotel_timezone,
                today=today,
            )
            with Session(engine) as session:
                available = check_availability(session, arrival_date, departure_date)
            st.session_state["available_range"] = (
                arrival_date,
                departure_date,
            ) if available else None
            if available:
                st.success("A room is available for these dates.")
            else:
                st.error("No room is available for the entire selected date range.")
        except ReservationError as error:
            st.session_state["available_range"] = None
            st.error(str(error))

    available_range = st.session_state.get("available_range")
    if not available_range or available_range != (arrival_date, departure_date):
        st.session_state.pop("confirmed_reservation", None)
        return

    arrival_date, departure_date = available_range
    st.subheader("Reservation details")
    with st.form("reservation_form"):
        cat_name = st.text_input("Cat name")
        breed = st.text_input("Breed")
        is_social = st.checkbox("My cat is social")
        daily_walks_required = st.checkbox("Daily walks required")
        st.write("Optional services")
        wellness_bath = st.checkbox("Wellness: bath")
        wellness_massage = st.checkbox("Wellness: massage")
        wellness_claw_trimming = st.checkbox("Wellness: claws trimming")
        premium_cat_food = st.checkbox("Premium cat food")
        confirm = st.form_submit_button("Confirm reservation")

    if confirm:
        st.session_state.pop("confirmed_reservation", None)
        try:
            with Session(engine) as session:
                reservation = create_reservation(
                    session,
                    arrival_date=arrival_date,
                    departure_date=departure_date,
                    cat_name=cat_name,
                    breed=breed,
                    is_social=is_social,
                    daily_walks_required=daily_walks_required,
                    hotel_timezone=settings.hotel_timezone,
                    wellness_bath=wellness_bath,
                    wellness_massage=wellness_massage,
                    wellness_claw_trimming=wellness_claw_trimming,
                    premium_cat_food=premium_cat_food,
                )
            st.session_state["confirmed_reservation"] = reservation
        except ReservationError as error:
            st.error(str(error))

    reservation = st.session_state.get("confirmed_reservation")
    if reservation:
        st.success("Your reservation is confirmed.")
        st.subheader(f"Reservation code: {reservation.display_code}")
        st.write(f"Cat: {reservation.cat_name} ({reservation.breed})")
        st.write(f"Stay: {reservation.arrival_date} to {reservation.departure_date}")
        if reservation.is_social:
            st.write("Social cat")
        if reservation.daily_walks_required:
            st.write("Daily walks required")
        selected_services = [
            label
            for enabled, label in (
                (reservation.wellness_bath, "Bath"),
                (reservation.wellness_massage, "Massage"),
                (reservation.wellness_claw_trimming, "Claws trimming"),
                (reservation.premium_cat_food, "Premium cat food"),
            )
            if enabled
        ]
        if selected_services:
            st.write("Optional services: " + ", ".join(selected_services))


def manage_reservation() -> None:
    st.header("Manage your reservation")
    try:
        settings, engine = _get_engine()
    except Exception as error:
        st.error(f"The booking service is not configured: {error}")
        return

    with st.form("lookup_form"):
        code = st.text_input("Reservation code", placeholder="123-456")
        lookup = st.form_submit_button("Find reservation")

    if lookup:
        with Session(engine) as session:
            reservation = get_reservation(session, code)
        if reservation is None:
            st.session_state.pop("managed_reservation_code", None)
            st.error("Reservation code could not be used.")
        else:
            st.session_state["managed_reservation_code"] = reservation.code

    reservation_code = st.session_state.get("managed_reservation_code")
    if not reservation_code:
        return
    with Session(engine) as session:
        reservation = get_reservation(session, reservation_code)
    if reservation is None:
        st.error("Reservation code could not be used.")
        return

    st.subheader(f"Reservation {reservation.display_code}")
    st.write(f"Status: {reservation.status.value}")
    st.write(f"Cat: {reservation.cat_name} ({reservation.breed})")
    st.write(f"Stay: {reservation.arrival_date} to {reservation.departure_date}")
    st.write(f"Social: {'Yes' if reservation.is_social else 'No'}")
    st.write(f"Daily walks required: {'Yes' if reservation.daily_walks_required else 'No'}")
    selected_services = [
        label
        for enabled, label in (
            (reservation.wellness_bath, "Bath"),
            (reservation.wellness_massage, "Massage"),
            (reservation.wellness_claw_trimming, "Claws trimming"),
            (reservation.premium_cat_food, "Premium cat food"),
        )
        if enabled
    ]
    st.write("Optional services: " + (", ".join(selected_services) if selected_services else "None"))

    if reservation.status == ReservationStatus.CANCELLED:
        if st.session_state.pop("just_cancelled", False):
            st.success(f"Reservation {reservation.display_code} is cancelled.")
        else:
            st.info("This reservation is cancelled.")
        return

    if can_leave_feedback(reservation, facility_today(settings.hotel_timezone)):
        show_feedback(engine, settings, reservation)
        return
    st.info(f"Feedback opens on your departure date ({reservation.departure_date}).")

    if not st.session_state.get("confirm_cancellation"):
        if st.button("Cancel reservation", type="secondary"):
            st.session_state["confirm_cancellation"] = True
            st.rerun()
        return

    st.warning("Are you sure you want to cancel this reservation?")
    confirm_col, keep_col = st.columns(2)
    if confirm_col.button("Confirm cancellation", type="primary"):
        try:
            with Session(engine) as session:
                cancelled = cancel_reservation(
                    session,
                    reservation.code,
                    hotel_timezone=settings.hotel_timezone,
                )
            st.session_state["just_cancelled"] = True
            st.session_state["confirm_cancellation"] = False
            st.session_state["managed_reservation_code"] = cancelled.code
            st.rerun()
        except ReservationError as error:
            st.session_state["confirm_cancellation"] = False
            st.error(str(error))
    if keep_col.button("Keep reservation"):
        st.session_state["confirm_cancellation"] = False
        st.rerun()



def show_feedback(engine, settings, reservation: Reservation) -> None:
    with Session(engine) as session:
        feedback = get_feedback(session, reservation)
    if feedback is None:
        st.subheader("How was your cat's stay?")
        with st.form("feedback_form"):
            rating = st.radio(
                "Rating (1 = poor, 5 = excellent)",
                [1, 2, 3, 4, 5],
                index=None,
                horizontal=True,
            )
            review = st.text_area("Short review (optional)", max_chars=REVIEW_MAX_LENGTH)
            send = st.form_submit_button("Send feedback")
        if not send:
            return
        try:
            with Session(engine) as session:
                submit_feedback(
                    session,
                    reservation.code,
                    rating,
                    review,
                    hotel_timezone=settings.hotel_timezone,
                )
        except FeedbackError as error:
            st.error(str(error))
            return
        st.rerun()

    st.success("Thank you for your feedback!")
    st.write(f"Your rating: {feedback.rating}/5")
    if feedback.review:
        st.write(feedback.review)


if __name__ == "__main__":
    main()
