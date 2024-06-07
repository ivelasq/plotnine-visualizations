import pandas as pd
from siuba import _, select, rename, filter, mutate, case_when, left_join
from dotenv import load_dotenv
load_dotenv()
import os

####################################
## 15- and 30-year mortgage rates ##
## Source: Freddie Mac            ##
####################################

from fredapi import Fred
fred = Fred(api_key=os.environ.get('FRED_KEY'))
mortgage30 = fred.get_series('MORTGAGE30US')
mortgage30 = mortgage30.to_frame(name=mortgage30)
mortgage30.reset_index(inplace=True)
mortgage30.columns = ['date', 'fixed_30']

mortgage15 = fred.get_series('MORTGAGE15US')
mortgage15 = mortgage15.to_frame(name=mortgage15)
mortgage15.reset_index(inplace=True)
mortgage15.columns = ['date', 'fixed_15']

rates_clean = mortgage30 >> left_join(_, mortgage15, on='date')
rates_clean.to_csv('data/rates_clean.csv', index=False)

##################################
## Vacancy Rates                ##
## Source: U.S. Census Bureau   ##
##################################

## Homeownership vacancies

file_path = 'data/raw/SeriesReport-202312011422-V.xlsx'
skip_rows = 7

home_vac = pd.read_excel(file_path, skiprows=skip_rows)

home_vacancies = (home_vac
    >> mutate(
        date = case_when(_, {
        _.Period.str.contains('1st Quarter'):  '01-01-' + _.Period.str[-4:],
        _.Period.str.contains('2nd Quarter'):  '01-04-' + _.Period.str[-4:],
        _.Period.str.contains('3rd Quarter'):  '01-07-' + _.Period.str[-4:],
        _.Period.str.contains('4th Quarter'):  '01-10-' + _.Period.str[-4:]
        })
    )
    >> select(
        _.date,
        _.Period,
        _.HousingVacancies == _.Value
    )
)

home_vacancies['date'] = pd.to_datetime(home_vacancies['date'], format='%d-%m-%Y')

## Rental Vacancy Rates

file_path = 'data/raw/SeriesReport-202312071711-V.xlsx'

rent_vac = pd.read_excel(file_path, skiprows=skip_rows)
rent_vac.columns = rent_vac.columns.str.replace('.','', regex=False)

rental_vacancies = (rent_vac
    >> mutate(
        date = case_when(_, {
        _.Period.str.contains('1st Quarter'):  '01-01-' + _.Period.str[-4:],
        _.Period.str.contains('2nd Quarter'):  '01-04-' + _.Period.str[-4:],
        _.Period.str.contains('3rd Quarter'):  '01-07-' + _.Period.str[-4:],
        _.Period.str.contains('4th Quarter'):  '01-10-' + _.Period.str[-4:]
        })
    )
    >> select(
        _.date,
        _.RentalVacancies == _.Value
    )
)

rental_vacancies['date'] = pd.to_datetime(rental_vacancies['date'], format='%d-%m-%Y')

vacancies = home_vacancies >> left_join(_, rental_vacancies, on='date')

vacancies.to_csv('data/vacancies.csv', index=False)

#########################################################
## Outstanding Mortgage Percent Share by Interest Rate ##
## Source: National Mortgage Database (NMDB)           ##
#########################################################

file_path = 'data/raw/nmdb-outstanding-mortgage-statistics-all-quarterly.csv'

out_mort = pd.read_csv(file_path)

var_list = ['PCT_INTRATE_LT_3', 'PCT_INTRATE_3_4', 'PCT_INTRATE_4_5', 'PCT_INTRATE_5_6', 'PCT_INTRATE_GE_6']

int_rate_share = (out_mort
    >> mutate(
        origin_int = case_when(_, {
        _.SERIESID == 'PCT_INTRATE_LT_3':  '<3%',
        _.SERIESID == 'PCT_INTRATE_3_4':   '3-4%',
        _.SERIESID == 'PCT_INTRATE_4_5':   '4-5%',
        _.SERIESID == 'PCT_INTRATE_5_6':   '5-6%',
        _.SERIESID == 'PCT_INTRATE_GE_6':  '>6%'
        })
    )
    >> filter(_.MARKET == 'All Mortgages',
              _.GEOID == 'USA',
              _.SERIESID.isin(var_list))
    >> mutate(
        date =  _.YEAR.apply(str) + "-" + _.MONTH.apply(str) + "-01",
        pct_share = _.VALUE1 / 100
    )
)

int_rate_share['date'] = pd.to_datetime(int_rate_share['date'])

int_rate_share.to_csv('data/int_rate_share.csv', index=False)