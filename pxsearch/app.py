from pxsearch.ls8l2 import ingest_LS8_L2_bucket_items


def main():
    print("Starting pxsearch")
    ingest_LS8_L2_bucket_items()


if __name__ == "__main__":  # Initiate boto session.
    main()
