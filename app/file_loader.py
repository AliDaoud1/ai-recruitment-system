from pathlib import Path
from services.file_helper import PDFLoader, normalize

DATA_DIR = Path("data")


def load_and_index(
        store,
        logger,
        security,
        pdf_reader,
        mode="analyzer",
        container=None,
):
    logger.log_print("=== Loading Candidate CVs ===")

    all_docs = []
    for path in DATA_DIR.glob("*"):
        if path.is_dir():
            continue

        logger.log_print(f"Processing file: {path.name}")

        if path.suffix == ".pdf":
            text = pdf_reader.load(str(path))
            docs = store.load_text(text, source=path.name)
        else:
            docs = store.load_file(str(path))

        for d in docs:
            report = security.detect(d.page_content)
            if report.emails or report.phones or report.links:
                logger.info(
                    f"PII detected in {path.name} | "
                    f"emails={len(report.emails)} "
                    f"phones={len(report.phones)} "
                    f"links={len(report.links)}"
                )
            d.page_content = security.sanitize(d.page_content)

        if mode == "analyzer":
            # global index (ALL CVs together)
            all_docs.extend(docs)

        elif mode == "hiring":
            namespace = normalize(path.stem).replace(" ", "_")

            store.index(
                documents=docs,
                namespace=namespace,
            )

            if container:
                container.namespace_manager.add(namespace)
            logger.info(f"Candidate indexed in namespace: {namespace}")

        logger.file_loaded(path.name, len(docs))
        logger.info(f"Chunks created: {len(docs)} for {path.name}")

    if mode == "analyzer":
        logger.log_print(f"Total chunks before indexing: {len(all_docs)}")
        store.index(all_docs)
        logger.indexing_done(len(all_docs))

    return all_docs
