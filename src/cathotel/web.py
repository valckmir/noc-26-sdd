from datetime import timedelta

import streamlit as st
from sqlmodel import Session

from cathotel.config import get_settings
from cathotel.database import create_database_engine, create_db_and_tables
from cathotel.services.dates import facility_today
from cathotel.services.reservations import (
    ReservationError,
    check_availability,
    create_reservation,
)


def _get_engine():
    settings = get_settings()
    engine = create_database_engine(settings.database_path)
    create_db_and_tables(engine)
    return settings, engine


def main() -> None:
    st.set_page_config(page_title="CatHotel", page_icon="🐈")
    st.title("Book a stay for your cat")
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
        if departure_date <= arrival_date:
            st.error("Departure date must be after arrival date.")
            st.session_state["available_range"] = None
        else:
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


if __name__ == "__main__":
    main()
