# Copilot Instructions for Solv-IT Django Application

## Project Overview
- This is a Django-based business management system for sales, inventory, billing, invoicing, and user/vendor/customer management.
- Major apps: `accounts`, `bills`, `invoice`, `store`, `transactions`.
- Frontend uses Bootstrap and Ajax for dynamic UI (notably in sales creation).
- Data flows through Django models, views, and templates; each app has its own models, views, and migrations.

## Key Workflows
- **Setup**: Use `python -m venv venv` and `pip install -r requirements.txt` (or `new_requirement.txt` if specified). Apply migrations with `python manage.py migrate`.
- **Run**: Start server via `python manage.py runserver`.
- **Docker**: Build with `docker build -t sales-and-inventory-management:1.0 .` and run with `docker run -d -p 8000:8000 sales-and-inventory-management:1.0`.
- **Testing**: Tests are in each app's `tests.py` (e.g., `accounts/tests.py`). Run with `python manage.py test <appname>`.

## Project-Specific Patterns
- **App Structure**: Each app contains `models.py`, `views.py`, `admin.py`, `tables.py`, `forms.py`, `urls.py`, and `templates/`.
- **Migrations**: All schema changes tracked in `migrations/` per app.
- **Templates**: HTML templates are organized under each app's `templates/` folder. Shared templates may be in `templates/` at the project root.
- **Static Files**: Located in `static/` (CSS, JS, images).
- **Signals**: Some apps (e.g., `accounts`, `transactions`) use Django signals for model event handling (`signals.py`).
- **Custom Filters/Tables**: Filtering and table display logic is in `filters.py` and `tables.py` per app.

## Integration Points
- **Ajax**: Used for dynamic sales creation and possibly other interactive features (see views and templates for usage).
- **Bootstrap**: For UI styling; check `static/css/` and templates for conventions.
- **Database**: Default is SQLite (`db.sqlite3`), but can be swapped via Django settings.

## Conventions & Tips
- **Naming**: Models, views, and forms follow Django conventions; custom logic is often in `filters.py`, `tables.py`, or `signals.py`.
- **Extending**: Add new business logic by creating new models/views in the relevant app and updating migrations/templates.
- **Debugging**: Use Django shell (`python manage.py shell`) and check logs/output for errors.
- **Requirements**: If `requirements.txt` is missing, check for `new_requirement.txt`.

## Example: Adding a New Model
1. Create model in `<app>/models.py`.
2. Run `python manage.py makemigrations <app>` and `python manage.py migrate`.
3. Register in `<app>/admin.py` if needed.
4. Add forms/views/templates as required.

## References
- Main entry: `manage.py`, project settings: `InventoryMS/settings.py`.
- For cross-app logic, see how `accounts`, `store`, and `transactions` interact via models and signals.

---
_If any section is unclear or missing, please provide feedback for further refinement._
