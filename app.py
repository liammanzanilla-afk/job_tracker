from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db
import json
import re

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret-key"


# Database table configuration
CONFIG = {
    "companies": {
        "table": "companies",
        "pk": "company_id",
        "title": "Companies",
        "columns": [
            "company_name", "industry", "website",
            "city", "state", "notes"
        ],
        "fields": [
            ("company_name", "Company Name", "text"),
            ("industry", "Industry", "text"),
            ("website", "Website", "url"),
            ("city", "City", "text"),
            ("state", "State", "text"),
            ("notes", "Notes", "textarea")
        ],
        "select": "SELECT * FROM companies"
    },

    "jobs": {
        "table": "jobs",
        "pk": "job_id",
        "title": "Jobs",
        "columns": [
            "company_id", "job_title", "job_type",
            "salary_min", "salary_max", "job_url",
            "date_posted", "requirements"
        ],
        "fields": [
            ("company_id", "Company", "company"),
            ("job_title", "Job Title", "text"),
            ("job_type", "Job Type", "job_type"),
            ("salary_min", "Minimum Salary", "number"),
            ("salary_max", "Maximum Salary", "number"),
            ("job_url", "Job URL", "url"),
            ("date_posted", "Date Posted", "date"),
            ("requirements", "Required Skills (JSON array)", "json")
        ],
        "select": """
            SELECT jobs.*, companies.company_name
            FROM jobs
            LEFT JOIN companies
            ON jobs.company_id = companies.company_id
        """
    },

    "applications": {
        "table": "applications",
        "pk": "application_id",
        "title": "Applications",
        "columns": [
            "job_id", "application_date", "status",
            "resume_version", "cover_letter_sent",
            "interview_data"
        ],
        "fields": [
            ("job_id", "Job", "job"),
            ("application_date", "Application Date", "date"),
            ("status", "Status", "status"),
            ("resume_version", "Resume Version", "text"),
            ("cover_letter_sent", "Cover Letter Sent", "checkbox"),
            ("interview_data", "Interview Data (JSON)", "json")
        ],
        "select": """
            SELECT applications.*, jobs.job_title
            FROM applications
            LEFT JOIN jobs ON applications.job_id = jobs.job_id
        """
    },

    "contacts": {
        "table": "contacts",
        "pk": "contact_id",
        "title": "Contacts",
        "columns": [
            "company_id", "contact_name", "title",
            "email", "phone", "linkedin_url", "notes"
        ],
        "fields": [
            ("company_id", "Company", "company"),
            ("contact_name", "Contact Name", "text"),
            ("title", "Job Title", "text"),
            ("email", "Email", "email"),
            ("phone", "Phone", "text"),
            ("linkedin_url", "LinkedIn URL", "url"),
            ("notes", "Notes", "textarea")
        ],
        "select": """
            SELECT contacts.*, companies.company_name
            FROM contacts
            LEFT JOIN companies
            ON contacts.company_id = companies.company_id
        """
    }
}


def get_companies():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT company_id, company_name FROM companies ORDER BY company_name"
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def get_jobs():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT job_id, job_title FROM jobs ORDER BY job_title"
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def get_form_options():
    return {
        "companies": get_companies(),
        "jobs": get_jobs()
    }


def prepare_value(value, field_type):
    if field_type == "checkbox":
        return 1 if value == "on" else 0

    if value == "":
        return None

    if field_type == "json":
        try:
            parsed = json.loads(value)
            return json.dumps(parsed)
        except (ValueError, TypeError):
            raise ValueError("Enter valid JSON.")

    if field_type == "number":
        return int(value)

    return value


def get_form_data(config):
    data = []

    for field, label, field_type in config["fields"]:
        raw_value = request.form.get(field, "")
        data.append(prepare_value(raw_value, field_type))

    return data


def get_all_stats():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    queries = {
        "companies": "SELECT COUNT(*) AS total FROM companies",
        "jobs": "SELECT COUNT(*) AS total FROM jobs",
        "applications": "SELECT COUNT(*) AS total FROM applications",
        "contacts": "SELECT COUNT(*) AS total FROM contacts"
    }

    stats = {}

    try:
        for key, query in queries.items():
            cursor.execute(query)
            stats[key] = cursor.fetchone()["total"]
    finally:
        cursor.close()
        conn.close()

    return stats


# Dashboard
@app.route("/")
def dashboard():
    stats = get_all_stats()

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT applications.application_id,
               applications.application_date,
               applications.status,
               jobs.job_title,
               companies.company_name
        FROM applications
        LEFT JOIN jobs ON applications.job_id = jobs.job_id
        LEFT JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY applications.application_date DESC
        LIMIT 5
    """)

    recent_applications = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_applications=recent_applications
    )


# Generic list, add, edit, and delete routes
@app.route("/<entity>")
def list_records(entity):
    if entity not in CONFIG:
        return "Page not found", 404

    config = CONFIG[entity]

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(config["select"])
    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        entity + ".html",
        records=records,
        config=config,
        entity=entity
    )


@app.route("/<entity>/add", methods=["GET", "POST"])
def add_record(entity):
    if entity not in CONFIG:
        return "Page not found", 404

    config = CONFIG[entity]

    if request.method == "POST":
        try:
            values = get_form_data(config)
            placeholders = ", ".join(["%s"] * len(values))
            columns = ", ".join(config["columns"])

            sql = (
                f"INSERT INTO {config['table']} "
                f"({columns}) VALUES ({placeholders})"
            )

            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(sql, values)
            conn.commit()
            cursor.close()
            conn.close()

            flash("Record added successfully!", "success")
            return redirect(url_for("list_records", entity=entity))

        except (ValueError, TypeError) as e:
            flash(str(e), "danger")
        except Exception:
            flash("Could not add record. Check your entries and database.", "danger")

    return render_template(
        "form.html",
        config=config,
        entity=entity,
        record={},
        options=get_form_options()
    )


@app.route("/<entity>/edit/<int:record_id>", methods=["GET", "POST"])
def edit_record(entity, record_id):
    if entity not in CONFIG:
        return "Page not found", 404

    config = CONFIG[entity]
    table = config["table"]
    pk = config["pk"]

    if request.method == "POST":
        try:
            values = get_form_data(config)
            assignments = ", ".join(
                [column + " = %s" for column in config["columns"]]
            )

            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {table} SET {assignments} WHERE {pk} = %s",
                values + [record_id]
            )
            conn.commit()

            cursor.close()
            conn.close()

            flash("Record updated successfully!", "success")
            return redirect(url_for("list_records", entity=entity))

        except (ValueError, TypeError) as e:
            flash(str(e), "danger")
        except Exception:
            flash("Could not update record. Check your entries and database.", "danger")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        f"SELECT * FROM {table} WHERE {pk} = %s",
        (record_id,)
    )
    record = cursor.fetchone()

    cursor.close()
    conn.close()

    if not record:
        return "Record not found", 404

    return render_template(
        "form.html",
        config=config,
        entity=entity,
        record=record,
        options=get_form_options()
    )


@app.route("/<entity>/delete/<int:record_id>", methods=["POST"])
def delete_record(entity, record_id):
    if entity not in CONFIG:
        return "Page not found", 404

    config = CONFIG[entity]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        f"DELETE FROM {config['table']} WHERE {config['pk']} = %s",
        (record_id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    flash("Record deleted successfully!", "success")
    return redirect(url_for("list_records", entity=entity))


# Job Match Feature
@app.route("/job_match", methods=["GET", "POST"])
def job_match():
    matches = []
    entered_skills = ""

    if request.method == "POST":
        entered_skills = request.form.get("skills", "")

        # Convert user skills into lowercase words
        user_skills = {
            skill.strip().lower()
            for skill in re.split(r"[,;\n]", entered_skills)
            if skill.strip()
        }

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT jobs.job_id, jobs.job_title,
                   jobs.requirements, companies.company_name
            FROM jobs
            LEFT JOIN companies
            ON jobs.company_id = companies.company_id
        """)

        jobs = cursor.fetchall()
        cursor.close()
        conn.close()

        for job in jobs:
            try:
                requirements = job["requirements"] or []
                if isinstance(requirements, str):
                    requirements = json.loads(requirements)

                if not isinstance(requirements, list):
                    continue

                required_skills = {
                    str(skill).strip().lower()
                    for skill in requirements
                    if str(skill).strip()
                }

                if not required_skills:
                    continue

                matched = user_skills.intersection(required_skills)
                missing = required_skills - user_skills

                percentage = round(
                    len(matched) / len(required_skills) * 100
                )

                job["matched_skills"] = sorted(matched)
                job["missing_skills"] = sorted(missing)
                job["percentage"] = percentage
                job["match_count"] = len(matched)
                job["total_skills"] = len(required_skills)

                matches.append(job)

            except (ValueError, TypeError):
                continue

        matches.sort(
            key=lambda item: item["percentage"],
            reverse=True
        )

    return render_template(
        "job_match.html",
        matches=matches,
        entered_skills=entered_skills
    )


if __name__ == "__main__":
    app.run(debug=True)
