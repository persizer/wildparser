# WildBerries scraper
Scraper for WildBerries. Scrape your way to victory!

## Table of Contents

- [About](#about)
- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)

## About

Scrapes WildBerries product categories. Fetches the amount of products, search count and average price for the past week and inputs the data into a MySQL database.

## Getting Started

These instructions will help you get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.10
- MySQL database
  
A good Windows package for that would be [XAMPP](https://www.apachefriends.org)

### Installation

A step-by-step guide:
```bash
git clone https://github.com/persizer/wildparser.git
cd wildparser
pip install -r requirements.txt
```
### Configuration

1. Rename `.env.sample` to `.env`
2. Change environment variables: 
   - `DB_HOST` to desired hostname
   - `DB_USER` to desired username
   - `DB_PASSWORD` to desired password
   - `DB_NAME` to desired database name

### Usage

```bash
# Example usage
python main.py
```
