# 🚀 AI Smart Basket: End-to-End Product Analytics & A/B Testing

### A Product Analytics Case Study Inspired by Modern Quick-Commerce Platforms

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![SQL](https://img.shields.io/badge/SQL-Analytics-orange?style=for-the-badge)
![Power BI](https://img.shields.io/badge/PowerBI-Dashboard-F2C811?style=for-the-badge&logo=powerbi)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas)
![NumPy](https://img.shields.io/badge/NumPy-Numerical%20Computing-013243?style=for-the-badge&logo=numpy)
![Statistics](https://img.shields.io/badge/A%2FB%20Testing-Statistics-success?style=for-the-badge)

---

## 📌 Project Overview

Modern quick-commerce platforms process millions of customer transactions every day. While customer acquisition has become increasingly efficient, improving **repeat purchases**, **customer retention**, and **basket value** remains one of the biggest product challenges.

This project presents an end-to-end **Product Analytics case study** centered around an AI-powered **Smart Basket** recommendation feature. The objective is to evaluate whether personalized basket recommendations can positively influence customer engagement, conversion, and revenue through structured analytics and experimentation.

Unlike traditional analytics projects that focus only on dashboards, this repository demonstrates the complete product analytics lifecycle—from data modeling and KPI definition to experimentation, statistical validation, and executive recommendations.

---

# 🎯 Business Problem

Quick-commerce platforms rely heavily on customer retention and repeat purchases to achieve long-term profitability. While users frequently purchase similar products every week, discovering and adding these items manually increases friction in the shopping journey.

A personalized **AI Smart Basket** recommendation system has the potential to:

- Reduce purchase friction
- Increase repeat purchase rate
- Improve Average Order Value (AOV)
- Enhance customer experience
- Increase customer lifetime value (CLV)

However, before deploying such a feature to millions of users, Product Managers must answer an important question:

> **"Will Smart Basket create measurable business value?"**

This project answers that question using Product Analytics, experimentation, and data-driven decision making.

---

# 🎯 Project Objectives

This project was designed to simulate the complete workflow of a Product Analytics team.

The major objectives include:

- Build an analytics-ready data model from raw marketplace data.
- Perform data quality assessment and validation.
- Define business and product KPIs.
- Analyze customer behavior and purchasing patterns.
- Identify high-value customer segments.
- Design a realistic Smart Basket product experiment.
- Evaluate feature performance using A/B testing.
- Validate experiment results using statistical hypothesis testing.
- Build an executive Power BI dashboard for business stakeholders.
- Deliver product recommendations backed by data.

---
# 🏗️ Product Analytics Workflow

This project follows an end-to-end Product Analytics lifecycle similar to the workflow used by analytics teams in modern technology companies.

```text
Business Problem
        │
        ▼
Data Collection
        │
        ▼
Data Quality Audit
        │
        ▼
Analytics Data Modeling
        │
        ▼
Feature Engineering
        │
        ▼
Product KPI Definition
        │
        ▼
Customer & Product Analytics
        │
        ▼
Experiment Design
        │
        ▼
A/B Testing
        │
        ▼
Statistical Validation
        │
        ▼
Business Recommendation
        │
        ▼
Executive Dashboard
```

---

# 🏛️ Project Architecture

```text
AI-Smart-Basket-Product-Analytics/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── 01_Data_Modeling.ipynb
│   ├── 02_Product_Analytics.ipynb
│   └── 03_AB_Testing.ipynb
│
├── dashboard/
│   └── Smart_Basket_Dashboard.pbix
│
├── sql/
│
├── docs/
│
├── images/
│
└── README.md
```

---

# ⚙️ Tech Stack

| Category | Technologies |
|----------|--------------|
| Programming | Python |
| Data Processing | Pandas, NumPy |
| Analytics | SQL |
| Visualization | Power BI |
| Experimentation | A/B Testing |
| Statistics | Hypothesis Testing |
| Version Control | Git & GitHub |
| Development Environment | VS Code, Jupyter Notebook |

---
# 📊 Dataset

This project uses the **Olist Brazilian E-Commerce Dataset**, one of the most widely used public datasets for marketplace analytics and product experimentation.

The dataset contains transactional information across multiple business entities, including:

- Customers
- Orders
- Order Items
- Products
- Sellers
- Payments
- Reviews
- Geolocation
- Product Category Translation

During the analytics pipeline, these datasets were transformed into a unified **analytics-ready master dataset** to support business reporting and experimentation.

> **Note:** The raw dataset is publicly available on Kaggle and has not been included in this repository to reduce repository size.

---

# 📈 Product Metrics

The following Product KPIs were developed and analyzed throughout the project.

| Category | Metrics |
|----------|---------|
| Growth Metrics | Monthly Revenue, Order Growth, Customer Growth |
| Customer Metrics | Repeat Purchase Rate, Customer Lifetime Value (CLV), Average Order Value |
| Product Metrics | Category Revenue, Product Ratings, Product Performance |
| Revenue Metrics | Total Revenue, Revenue per Customer, Revenue Lift |
| Engagement Metrics | Repeat Customers, Purchase Frequency |
| Experiment Metrics | CTR, Conversion Rate, Revenue Lift, Statistical Significance |

---

# 🧪 Smart Basket Experiment

A simulated **AI Smart Basket recommendation feature** was designed to evaluate the business impact of personalized shopping recommendations.

The experiment follows a classic **A/B Testing** framework.

### Control Group

- Existing shopping experience
- No Smart Basket recommendations

### Treatment Group

- AI Smart Basket recommendations enabled
- Personalized product suggestions
- Simplified repeat purchase experience

The experiment evaluates whether introducing Smart Basket improves:

- Click Through Rate (CTR)
- Purchase Conversion Rate
- Average Revenue per User
- Repeat Purchase Behaviour

Statistical hypothesis testing is then performed to determine whether the observed improvements are statistically significant.

---
# 💡 Key Business Insights

The analysis produced several business insights that can support product and growth decisions.

### Customer Insights

- A relatively small segment of customers contributes a significant share of overall revenue.
- Repeat customers generate substantially higher lifetime value than one-time purchasers.
- Customer ratings remain consistently high, indicating strong product satisfaction.

### Product Insights

- Revenue is concentrated within a limited number of product categories.
- High-performing categories represent the best opportunity for recommendation optimization.
- Product ratings and purchase volume show positive correlation across several categories.

### Revenue Insights

- Monthly revenue demonstrates strong growth over the observed period.
- Average Order Value remains stable, providing a reliable baseline for experimentation.
- Customer acquisition and repeat purchasing both contribute to overall business growth.

---

# 🚀 Business Recommendations

Based on the analysis and experimentation, the following recommendations are proposed:

### Recommendation 1

Roll out the Smart Basket feature initially to **high-value repeat customers**, as they are the most likely to engage with personalized recommendations.

### Recommendation 2

Continuously monitor:

- Click Through Rate (CTR)
- Conversion Rate
- Average Order Value (AOV)
- Revenue Lift
- Repeat Purchase Rate

after deployment.

### Recommendation 3

Conduct phased rollouts rather than a full-scale release to minimize business risk and validate experiment results across different customer segments.

### Recommendation 4

Expand personalization by incorporating customer purchase history and category preferences into future recommendation models.

---

# 📊 Dashboard Preview

The Power BI dashboard developed as part of this project provides an executive view of business performance through interactive visualizations.

Dashboard pages include:

- 📈 Executive Overview
- 👥 Customer Analytics
- 📦 Product Analytics
- 🧪 Smart Basket Experiment
- 📊 Business Recommendations

> Dashboard screenshots will be added after final dashboard development.

---
# 🔮 Future Enhancements

The current implementation establishes a strong Product Analytics foundation. Future improvements may include:

- 🤖 Machine Learning–based recommendation engine
- 🧠 Personalized ranking using collaborative filtering
- ⚡ Real-time event streaming and analytics
- 🎯 Customer churn prediction
- 🎁 Coupon and promotion personalization
- 📱 Real-time feature monitoring dashboard
- 📊 Advanced cohort and retention analysis

---

# ▶️ How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/Aqdas999/AI-Smart-Basket-End-to-End-Product-Analytics-Experimentation.git
```

### 2. Navigate to the Project

```bash
cd AI-Smart-Basket-End-to-End-Product-Analytics-Experimentation
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the Jupyter Notebooks

```bash
jupyter notebook
```

### 5. Open the Power BI Dashboard

Open:

```text
dashboard/Smart_Basket_Dashboard.pbix
```

---

# 📂 Repository Structure

```text
AI-Smart-Basket-End-to-End-Product-Analytics-Experimentation/

├── dashboard/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── images/
├── notebooks/
├── sql/
├── README.md
├── requirements.txt
└── LICENSE
```

---

# 🎓 Skills Demonstrated

- Product Analytics
- Business Analytics
- Product Thinking
- A/B Testing
- Statistical Hypothesis Testing
- SQL Analytics
- Python (Pandas & NumPy)
- Data Cleaning & Feature Engineering
- Power BI Dashboard Development
- Executive Reporting
- Data Visualization
- Git & GitHub

---

# ⭐ Key Takeaways

This project demonstrates how Product Analytics can be used to move beyond descriptive reporting and support data-driven product decisions.

Rather than focusing solely on dashboards, the project follows a structured analytics workflow—from understanding the business problem and preparing analytics-ready data to designing experiments, validating results statistically, and communicating actionable recommendations.

The end result is a complete Product Analytics case study that mirrors how modern product teams evaluate and launch new features.

---

