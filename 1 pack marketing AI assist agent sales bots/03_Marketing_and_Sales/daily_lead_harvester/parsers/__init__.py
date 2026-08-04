from .hh_parser import fetch_hh_leads
from .adata_parser import fetch_adata_leads
from .threads_parser import fetch_threads_leads

def run_all_parsers(queries_dict):
    """
    Агрегатор сбора со всех 4 источников:
    - adata.kz
    - hh.ru
    - hh.kz
    - threads.net
    """
    all_leads = []

    # 1. HH.kz (Казахстан)
    hh_kz_leads = fetch_hh_leads(queries_dict.get("hh", []), area_id=40, source_label="hh.kz")
    all_leads.extend(hh_kz_leads)

    # 2. HH.ru (Россия)
    hh_ru_leads = fetch_hh_leads(queries_dict.get("hh", []), area_id=113, source_label="hh.ru")
    all_leads.extend(hh_ru_leads)

    # 3. Adata.kz (Казахстан)
    adata_leads = fetch_adata_leads(queries_dict.get("targets", []))
    all_leads.extend(adata_leads)

    # 4. Threads.net
    threads_leads = fetch_threads_leads(queries_dict.get("threads", []))
    all_leads.extend(threads_leads)

    return all_leads
