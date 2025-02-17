import asyncio
import os
from datetime import date, timedelta
import pandas as pd
import asyncpg
from pathlib import Path
import os
from dotenv import load_dotenv
print(os.path.dirname(__file__))
dotenv_path = os.path.join(os.path.dirname(__file__), "db1.env")

if not os.path.exists(dotenv_path):
    raise Exception(".env file does not exist")

load_dotenv(dotenv_path)


class SystemConfig:
    def __init__(self):
        self.remote_db_user = os.getenv("REMOTE_DB_USER")
        self.remote_db_password = os.getenv("REMOTE_DB_PASSWORD")
        self.remote_db_host = os.getenv("REMOTE_DB_HOST")
        self.remote_db_name = os.getenv("REMOTE_DB_NAME")
        self.remote_db_port = os.getenv("REMOTE_DB_PORT")
        self.shst_path = os.getenv("SHST_FOLDER")
        self.crawl_db_user = os.getenv("CRAWL_DB_USER")
        self.crawl_db_password = os.getenv("CRAWL_DB_PASSWORD")
        self.crawl_db_host = os.getenv("CRAWL_DB_HOST")
        self.crawl_db_name = os.getenv("CRAWL_DB_NAME")
        self.crawl_db_port = os.getenv("CRAWL_DB_PORT")
        self.remote_db_async_url = f"postgresql://{self.remote_db_user}:{self.remote_db_password}@{self.remote_db_host}:{self.remote_db_port}/{self.remote_db_name}"
        self.crawl_db_async_url = f"postgresql://{self.crawl_db_user}:{self.crawl_db_password}@{self.crawl_db_host}:{self.crawl_db_port}/{self.crawl_db_name}"
        self.db_async_url = f"postgresql://{self.crawl_db_user}:{self.crawl_db_password}@{self.crawl_db_host}:{self.crawl_db_port}/{self.crawl_db_name}"
        self.sftp_server = os.getenv("SFTP_SERVER")
        self.sftp_user = os.getenv("SFTP_USER")
        self.sftp_password = os.getenv("SFTP_PASSWORD")
        self.sftp_path = os.getenv("SFTP_PATH")

        self.conn = None
        self.remote_conn = None


system_config = SystemConfig()


def run_async(func):
    async def wrapper(*args, **kwargs):
        system_config.conn = await asyncpg.connect(system_config.db_async_url)
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print(e)
        finally:
            await system_config.conn.close()

    return wrapper


def get_date_constraint(weekday: int, export_date: str) -> str:
    return (
        f"= '{export_date}'::date - INTERVAL '1 day' "
        #f"between '{export_date}'::date - INTERVAL '3 day' and '{export_date}'::date + INTERVAL '1 day'"
        if weekday != 1
        else f"between '{export_date}'::date - INTERVAL '3 day' and '{export_date}'::date - INTERVAL '1 day'"
    )


async def collect_new_events(
        weekday: int, search_constraint: str,
        export_date: str,
) -> pd.DataFrame:
    date_constraint = get_date_constraint(weekday=weekday, export_date=export_date)
    query = f"""
    select article_date, 
    CASE WHEN article_location ilike '%(ots)%' THEN substring(trim(article_location) for length(trim(article_location))-6) 
    ELSE article_location END as article_location, 
    article_state, article_title, article_text 
    from ergo.events_selenium 
    where {search_constraint}
    and article_date {date_constraint}
    """
    stmt = await system_config.conn.prepare(query)
    columns = [a.name for a in stmt.get_attributes()]
    data = await stmt.fetch()
    return pd.DataFrame(data, columns=columns)


async def collect_new_events1(
        weekday: int, search_constraint: str,
        export_date: str,
) -> pd.DataFrame:
    date_constraint = get_date_constraint(weekday=weekday,export_date=export_date)
    query = f"""WITH streetnames as (
select article_id, STRING_AGG(article_words,', ') as article_strnames
from (
select distinct article_id, article_words
from (
select article_id, 
unnest(STRING_TO_ARRAY(regexp_replace(replace(article_text,E'\n',' '), '[^a-zA-ZäöüÄÖÜß\- ]', '', 'g'), ' ')) as article_words
from ergo.events_selenium
where article_date {date_constraint}
) x1
where article_words ilike ANY(ARRAY['%straße','%str','%platz','%weg','%allee','%gasse'])
and not article_words ilike ANY(ARRAY['straße','str','bundesstraße','landstraße','landesstraße',
'kreisstraße','einbahnstraße','staatsstraße','%verbindungsstraße','%umgehungsstraße','bundestraße',
'vorfahrtsstraße','vorfahrtstraße','seitenstraße','spielstraße','%zufahrt%','gemeindestraße',
'fahrradstraße','querstraße','%durchgang%','platz','%parkplatz','%spielplatz','marktplatz',
'%sportplatz','%rastplatz','%stellplatz','campingplatz','flugplatz','festplatz','%vorplatz',
'lagerplatz','%grillplatz','%arbeitsplatz','%übungsplatz','dorfplatz','sitzplatz','golfplatz',
'weg','%radweg','feldweg','gehweg','%fußgänger%','fußweg','waldweg','heimweg','postweg','steinweg',
'%verbindungsweg','hinweg','nachhauseweg','rückweg','schulweg','mittelweg','durchweg','einstiegsweg',
'holzweg','fluchtweg','forstweg','%überweg','fahrweg','bremsweg','landweg','ausweg','anhalteweg',
'querweg','rundweg','vorweg','allee','gasse','sackgasse','rettungsgasse','seitengasse'])
) x2
group by article_id
)
select article_date, 
CASE WHEN article_location ilike '%(ots)%' THEN substring(trim(article_location) for length(trim(article_location))-6) 
ELSE article_location END
as article_location, 
article_state,
article_title, article_text 
--, article_strnames
from ergo.events_selenium x1
--left join streetnames y1
--on x1.article_id = y1.article_id
where {search_constraint}
and article_date {date_constraint}"""
    stmt = await system_config.conn.prepare(query)
    columns = [a.name for a in stmt.get_attributes()]
    data = await stmt.fetch()
    return pd.DataFrame(data, columns=columns)


def output_excel_file(df: pd.DataFrame, filename_suffix: str = "", export_date: str = date.today().isoformat()):
    filename_date = date.fromisoformat(export_date).strftime("%Y%m%d")
    filename = os.path.join(
        system_config.shst_path,
        f"{filename_date}_ergo_events{filename_suffix}.xlsx",
    )
    df.to_excel(filename, index=False)
    return filename


@run_async
async def main(export_date: str =  (date.today() - timedelta(days=6)).isoformat()):
    export_date_date: date = date.fromisoformat(export_date)
    weekday = export_date_date.isoweekday()

    # search_break_in = """article_text ilike ANY(ARRAY['% einbruch%', '%einbrecher%', '%einbrüche%', '%eingebrochen%', 
    # '%einbrechen%'])"""
    # search_fire = """article_text ilike ANY(ARRAY['%wohnungsbrand%', '%wohnungsbrände%', '%hausbrand%', 
    # '%hausbrände%', '% brand %', '%brandursache%']) and not article_text ilike ANY(ARRAY['%fahrzeugbrand%', 
    # '%fahrzeugbrände%', '% im brand%', '%waldbrand%'])"""
    # search_bike = """article_text ilike ANY(ARRAY['%diebstahl%','%diebstähle%','%gestohlen%','%stehlen%','%unfall%',
    # '%unfälle%']) and article_text ilike ANY(ARRAY['%fahrrad%','%fahrräder%','%mountainbike%','%rennrad%','%e-bike%',
    # '%pedelec%','%herrenrad%','%damenrad%'])"""
    # search_traffic_accident = """(article_text ilike ANY(ARRAY[
    # '%verkehrsunfall%', '%verkehrsunfälle%', '%autounfall%', '%autounfälle%', 
    # '%fahrradunfall%', '%fahrradunfälle%', '%motorradfahrer% unfall%', '%fahrradfahrer% unfall%', '%autofahrer% unfall%'
    # '%auffahrunfall%', '%unfallflucht%', '%unfall unter Alkoholeinfluss%',  '%fahrer% kollision%']) OR article_title ~* 'vorfahrt missachtet')
    
    # """
    search_arbeit_accident = """ article_title ~* 'arbeit unfall'
    """
    search_freizeit_accident = """ article_title ~* 'freizeit unfall'
    """
    
    search_haushalt_accident = """ article_title ~* 'haushalt unfall'
    """
   


    # Collect and save for each type of event
    # df = await collect_new_events(weekday, search_break_in, export_date=export_date)
    # output_filename_break_in = output_excel_file(df=df, export_date=export_date)

    # df = await collect_new_events(weekday, search_fire, export_date=export_date)
    # output_filename_fire = output_excel_file(df=df, filename_suffix="_brand", export_date=export_date)

    # df = await collect_new_events(weekday, search_bike, export_date=export_date)
    # output_filename_bike = output_excel_file(df=df, filename_suffix="_fahrrad", export_date=export_date)

    # df = await collect_new_events(weekday, search_traffic_accident, export_date=export_date)
    # output_filename_traffic = output_excel_file(df=df, filename_suffix="_traffic", export_date=export_date)

    df = await collect_new_events(weekday, search_arbeit_accident, export_date=export_date)
    output_filename_work = output_excel_file(df=df, filename_suffix="_arbeit", export_date=export_date)
    
    df = await collect_new_events(weekday, search_freizeit_accident, export_date=export_date)
    output_filename_work = output_excel_file(df=df, filename_suffix="_freizeit", export_date=export_date)
    
    df = await collect_new_events(weekday, search_haushalt_accident, export_date=export_date)
    output_filename_work = output_excel_file(df=df, filename_suffix="_haushalt", export_date=export_date)



if __name__ == "__main__":
    asyncio.run(main())
    
    
     