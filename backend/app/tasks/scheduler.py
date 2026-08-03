import logging
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import text
from app.core.database import get_engine

logger = logging.getLogger(__name__)

def processar_substituicoes_job():
    """
    Job diário que lê a tabela fun_cobranca_substituicoes
    e atualiza os status na tabela fun_funcionarios_cobranca
    de acordo com as datas.
    """
    logger.info("Executando job diário: processar_substituicoes_job")
    
    for dbname in ["SicoobSMO", "LeCom"]:
        engine = get_engine(dbname)
        try:
            with engine.begin() as conn:
                # 1. Ativar substitutos cujo período iniciou (e inativar originais)
                # Status vai de AGENDADA para EM_ANDAMENTO
                conn.execute(text("""
                    UPDATE public.fun_funcionarios_cobranca
                    SET status = 1
                    WHERE id IN (
                        SELECT substituto_id FROM public.fun_cobranca_substituicoes
                        WHERE status_substituicao = 'AGENDADA'
                          AND CURRENT_DATE BETWEEN data_inicio AND data_fim
                    )
                """))
                
                conn.execute(text("""
                    UPDATE public.fun_funcionarios_cobranca
                    SET status = 0
                    WHERE id IN (
                        SELECT original_id FROM public.fun_cobranca_substituicoes
                        WHERE status_substituicao = 'AGENDADA'
                          AND CURRENT_DATE BETWEEN data_inicio AND data_fim
                    )
                """))
                
                conn.execute(text("""
                    UPDATE public.fun_cobranca_substituicoes
                    SET status_substituicao = 'EM_ANDAMENTO'
                    WHERE status_substituicao = 'AGENDADA'
                      AND CURRENT_DATE BETWEEN data_inicio AND data_fim
                """))
                
                # 2. Inativar substitutos cujo período terminou (e reativar originais)
                # Status vai de EM_ANDAMENTO para CONCLUIDA
                conn.execute(text("""
                    UPDATE public.fun_funcionarios_cobranca
                    SET status = 0
                    WHERE id IN (
                        SELECT substituto_id FROM public.fun_cobranca_substituicoes
                        WHERE status_substituicao = 'EM_ANDAMENTO'
                          AND CURRENT_DATE > data_fim
                    )
                """))
                
                conn.execute(text("""
                    UPDATE public.fun_funcionarios_cobranca
                    SET status = 1
                    WHERE id IN (
                        SELECT original_id FROM public.fun_cobranca_substituicoes
                        WHERE status_substituicao = 'EM_ANDAMENTO'
                          AND CURRENT_DATE > data_fim
                    )
                """))
                
                conn.execute(text("""
                    UPDATE public.fun_cobranca_substituicoes
                    SET status_substituicao = 'CONCLUIDA'
                    WHERE status_substituicao = 'EM_ANDAMENTO'
                      AND CURRENT_DATE > data_fim
                """))
                
        except Exception as e:
            logger.error(f"Erro ao processar substituições no DB {dbname}: {e}")

scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(processar_substituicoes_job, 'cron', hour=0, minute=1)
    scheduler.start()
    logger.info("APScheduler iniciado.")

def shutdown_scheduler():
    scheduler.shutdown()
    logger.info("APScheduler desligado.")
