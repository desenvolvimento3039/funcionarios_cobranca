import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.repositories.substituicao_repository import SQLSubstituicaoRepository

logger = logging.getLogger("uvicorn.error")

def processar_substituicoes_job():
    """
    Job de processamento da escala de substituições.
    Atualiza status das substituições agendadas e concluídas.
    """
    logger.info("Executando job: processar_substituicoes_job")
    db = SessionLocal()
    try:
        repo = SQLSubstituicaoRepository(db)
        stats = repo.process_scheduled_substitutions()
        logger.info(f"[Scheduler] Processamento concluído: {stats}")
    except Exception as e:
        logger.error(f"[Scheduler] Erro ao processar substituições: {e}")
    finally:
        db.close()

scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(processar_substituicoes_job, 'cron', hour=0, minute=1)
    scheduler.start()
    logger.info("APScheduler iniciado.")

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler desligado.")
