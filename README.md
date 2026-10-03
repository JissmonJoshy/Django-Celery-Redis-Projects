# Django-Celery-Redis-Projects

A collection of Django projects demonstrating asynchronous backend architecture using 
Celery and Redis for background task processing. Covers REST API design with Django 
REST Framework, MariaDB/MySQL integration, resumable batch processing for large datasets, 
and role-based access control.

## Projects

### Shopify Product Taxonomy Classification System
An AI-assisted product classification platform that automatically maps a product catalogue 
(10,000+ items) to Shopify's product taxonomy. Built with Django, MariaDB, Celery, and Redis 
for background classification jobs, and Django REST Framework for a paginated API. Uses 
TF-IDF text similarity (scikit-learn) to predict product categories with confidence scores 
and alternative suggestions, with a review/approval workflow for Admin and Reviewer roles. 
Handles missing product data and broken images gracefully without stopping batch processing, 
and supports resumable background jobs so interrupted runs continue from where they left off 
instead of restarting.

**Tech stack:** Python, Django, Django REST Framework, MariaDB, Celery, Redis, Docker, 
Bootstrap, scikit-learn, openpyxl
