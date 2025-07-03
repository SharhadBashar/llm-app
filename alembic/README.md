# Alembic 

## Files and Folder structure
```
alembic/
├── versions/                           # Contains all migration files
│   ├── 001_initial_migration.py
│   ├── 002_add_user_table.py
│   └── 003_add_email_column.py
├── alembic.ini                         # Main configuration file (in project root)
├── env.py                              # Migration environment configuration
├── script.py.mako                      # Template for new migrations
└── README.md                           # Optional readme file
```
- `versions`<br>
The versions/ folder contains all your migration files, named with a revision ID prefix<br>
These contain all the changes to the db, including the new model changes<br>
Each migration has upgrade() and downgrade() functions that define how to apply and revert changes<br>

- `alembic.ini`
Main configuration file that tells it how to connect to your database and where to find migration scripts.<br>
It primarily contains the database connection URL, the path to your migration files, logging settings to control output verbosity, and optional formatting rules for generated migration filenames.

- `env.py`<br>
Configures how Alembic runs migrations by setting up the database connection and linking your SQLAlchemy models' metadata.<br>
It contains two main functions - `run_migrations_offline()` for generating SQL scripts without a database connection, and `run_migrations_online()` for directly executing migrations against a live database, with the script automatically choosing which mode to use based on the context.

- `script.py.mako`
Template for new migrations

## Process
### Upgrade
1. Create a new model
2. Add it to `core/__init__.py`
3. Run `alembic revision --autogenerate -m 'fixed migration description'` to create a new file in `versions` folder
4. Double check to make sure all the columns are correct, as well as verify the `upgrade()` and `downgrade()` functions
5. Run `alembic upgrade head` to apply new migration

### Downgrade
🚨 First check the downgrade function in versions file to make sure any Enums or types that were created are also dropped 🚨
1. Run `alembic downgrade -1`
2. Delete latest file in versions
3. Make changes to model
4. Run steps 3 - 5 in the Upgrade section

## Commands

### Most commonly used Commands
- `alembic revision --autogenerate -m 'description of changes'`<br>
Auto-generate migration from model changes<br>
Run this after you create a new model. Make sure to add the models to `core/__init__.py`

- `alembic upgrade head`<br>
Upgrade to latest version

- `alembic downgrade -1`<br>
Downgrade to previous

### Commands
- `alembic init alembic`<br>
Initialize Alembic

- `alembic revision -m 'description of changes'`<br>
Create a new migration

- `alembic revision --autogenerate -m 'description of changes'`<br>
Auto-generate migration from model changes<br>
Run this after you create a new model. Make sure to add the models to `core/__init__.py`

#### Apply Migrations
- `alembic upgrade head`<br>
Upgrade to latest version

- `alembic upgrade <revision>`<br>
Upgrade to specific revision

- `alembic upgrade +1`<br>
Upgrade one step

#### Downgrade Migrations
- `alembic downgrade -1`<br>
Downgrade to previous

- `alembic downgrade <revision>`<br>
Downgrade to specific revision

- `alembic downgrade base`<br>
Downgrade to base (remove all)

#### Information
- `alembic current`<br>
Show current revision

- `alembic history`<br>
Show migration history

- `alembic history -v`<br>
Show verbose migration history

- `alembic show <revision>`<br>
Show specific revision info
