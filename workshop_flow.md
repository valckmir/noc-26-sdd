# CatHotel

## Constitution

The CatHotel is a web application for bookoing rooms for cats. It's main advantage is simplicity, minimalism and user centric design. All features brings a real value.

There are two roles: customer (cat owner) and staff.

Architecture is layered - whole business logic is implemented in services - never in views. The implementation must be simple, never complex. Simple is always better than complex. Reasonable limitations are acceptable.

If there are comments in the code, they are ther only to explain why is something done in such way - never what and how!

## Specify

Develop a web application for cat owner to let them book rooms for cats. Customers must be able to pick a date range. There is only one type of rooms, therefore there is no need for room listing and room type selection.

If there is any room available, customers are prompted to add more reservation details:

- cat name
- breed
- social or not
- daily walks required

Moreover, customers can select any of optional services:

- wellness (bath, massage, claws trimming)
- premium cat food

Room availability/capacity is provided by staff - by uploading CSV file consisting of two columns: date and room capacity.

Entire process is accountless - no registrations and logins are supported.

After confirming and sending reservation request, the app generates unique reservation code. This code is then used for reservation management, i.e. showing details of reservation or cancelling it. Modifications are not allowed. Reservations are effective immediately - no humen confirmation is required.

No notification is sent. All information is shown only in the application.


## Clarify

- UI must not allow users to pick a past date
- cancellation is possible until 2 calendar days before check-in
- reservation code must be 6 digits split in 2 group separated with "-"


## Plan

Implement the app with the streamlit framework. Web interface is for customers, staff uses python typer commands for CSV upload.
Data is stored in SQLite DB, SQLModel is used as ORM and for business models. Pydantic settings with .env file is used for configuration.

The uv is used for dependency management.

## Tasks

(no args)

## Analyze

(no args)
resolve identified issues one by one

## Implement

phase by phase


## Converge

(no args)