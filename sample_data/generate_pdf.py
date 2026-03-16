#!/usr/bin/env python3
"""Generate a sample PDF bank statement for testing."""

import os

def create_sample_pdf():
    """Create a simple text-based PDF bank statement."""
    content = """
FIRST NATIONAL BANK
Monthly Account Statement
=====================================
Account Holder: Alex Johnson
Account Number: ****4821
Statement Period: January 1 - February 28, 2024
=====================================

TRANSACTION HISTORY

Date          Description                         Amount      Balance
--------------------------------------------------------------------------
01/02/2024    Salary Deposit - TechCorp Inc       +4,500.00   4,500.00
01/03/2024    Whole Foods Market                    -127.45   4,372.55
01/04/2024    Netflix Subscription                   -15.99   4,356.56
01/05/2024    Uber Ride to Office                    -18.50   4,338.06
01/06/2024    Starbucks Coffee                        -6.75   4,331.31
01/07/2024    Amazon Purchase - Books                -42.30   4,289.01
01/08/2024    Planet Fitness Monthly                 -24.99   4,264.02
01/09/2024    Shell Gas Station                      -65.00   4,199.02
01/11/2024    Chipotle Mexican Grill                 -13.85   4,185.17
01/12/2024    Spotify Premium                         -9.99   4,175.18
01/13/2024    Rent Payment - Oakwood Apts         -1,400.00   2,775.18
01/14/2024    Uber Eats - McDonald's                 -28.60   2,746.58
01/15/2024    Target Store                           -89.75   2,656.83
01/16/2024    Freelance Payment - DesignCo          +800.00   3,456.83
01/17/2024    Comcast Internet                       -74.99   3,381.84
01/18/2024    Trader Joe's                           -93.20   3,288.64
01/19/2024    Lyft Ride                              -12.30   3,276.34
01/20/2024    Hulu + Live TV                         -76.99   3,199.35
01/22/2024    Cheesecake Factory                     -67.40   3,131.95
01/24/2024    Home Depot                            -145.60   2,986.35
01/25/2024    Starbucks Coffee                        -5.25   2,981.10
01/27/2024    AMC Movie Theaters                     -32.50   2,948.60
01/28/2024    Electric Bill - ConEd                 -112.30   2,836.30
01/29/2024    Whole Foods Market                    -105.80   2,730.50
01/30/2024    GrubHub - Thai Palace                  -35.20   2,695.30
02/01/2024    Salary Deposit - TechCorp Inc       +4,500.00   7,195.30
02/03/2024    Costco Membership                      -65.00   7,130.30
02/04/2024    Sephora                                -78.50   7,051.80
02/05/2024    Panera Bread                           -14.25   7,037.55
02/07/2024    Lyft Ride                              -15.60   7,021.95
02/08/2024    Doctor Visit Copay                     -40.00   6,981.95
02/09/2024    Zara Clothing                         -156.75   6,825.20
02/12/2024    AT&T Phone Bill                        -85.00   6,740.20
02/13/2024    Uber Eats - Pizza Hut                  -31.40   6,708.80
02/14/2024    Valentine's Dinner - Nobu             -210.00   6,498.80
02/15/2024    Freelance Payment - StartupXYZ      +1,200.00   7,698.80
02/16/2024    Trader Joe's                           -87.60   7,611.20
02/17/2024    Shell Gas Station                      -58.30   7,552.90
02/18/2024    Rent Payment - Oakwood Apts         -1,400.00   6,152.90
02/20/2024    LinkedIn Premium                       -39.99   6,112.91
02/22/2024    Nike Store                            -125.00   5,987.91
02/24/2024    Starbucks Coffee                        -7.10   5,980.81
02/26/2024    Disney+ Subscription                   -13.99   5,966.82

--------------------------------------------------------------------------
ACCOUNT SUMMARY
Total Credits:     $11,000.00
Total Debits:       $5,033.18
Closing Balance:    $5,966.82
--------------------------------------------------------------------------
This statement is for informational purposes only.
For questions, call 1-800-FNB-HELP
"""
    
    # Write as a text file that mimics a PDF bank statement
    # Since we can't install fpdf2 without network, we'll create a text version
    # that pdfplumber can handle if it were a real PDF
    # For demo purposes, we create the CSV which is the primary test file
    
    with open("sample_data/sample_statement_content.txt", "w") as f:
        f.write(content)
    
    print("Sample bank statement content created!")
    print("Note: Use sample_statement.csv for testing - it has 50 realistic transactions.")
    print("The PDF generator requires fpdf2 - install with: pip install fpdf2")

if __name__ == "__main__":
    create_sample_pdf()
