# Streamlit прототип: филиалы → расход топлива → консолидация → расчет CO2 по МПР 371

## Быстрый старт
```bash
cd app
pip install -r ../requirements.txt
streamlit run Home.py
```

## Демо-учетки
- admin / adminpass (администратор)
- user1 / userpass (филиал Котлас)
- user2 / userpass (филиал Архангельск)

## Где лежит справочник
`app/data/tblEF_371.csv`

## Формула
CO2_kg = qty * LHV * EF_CO2
CO2_t  = CO2_kg / 1000

> В прототипе предполагается, что LHV и EF_CO2 согласованы по единицам (как в вашей практической схеме Q×НТС×EF_CO2).
> Если в вашей таблице EF_CO2 задан в других единицах — поправьте `app/core/calc.py`.
