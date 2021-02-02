import signal
from datetime import datetime

from tqdm import tqdm

import yticker

terminate = False


def signal_handling(signum, frame):
    global terminate
    if terminate:
        exit(1)
    else:
        print("Terminate gracefully...")
        terminate = True


def main(saved='YahooTickerDownloader.pickle'):
    try:
        ytd = yticker.YahooTickerDownloader.load(saved)
        print("Resume the downloader found on disk.")
    except Exception:
        ytd = yticker.YahooTickerDownloader()
        print("Start a brand new downloader.")

    pbar = tqdm(total=ytd.queue_length)

    while not ytd.done:
        pbar.set_description(f"[query = {ytd.peak_query}]")
        pbar.refresh()

        t = datetime.now()
        key, count, total = ytd.download_next()
        seconds = (datetime.now() - t).total_seconds()
        pbar.write(f"query = {key} | count = {count} | total = {total} | seconds = {seconds}")
        pbar.total = ytd.queue_length
        pbar.n = ytd.index
        pbar.refresh()

        if ytd.index % 20 == 0 or ytd.done or terminate:
            ytd.save(saved)
            pbar.write("Downloader saved to disk.")
            if terminate:
                pbar.close()
                return

    pbar.close()
    df = ytd.get_dataframe()
    df.to_csv('answers.csv')


if __name__ == "__main__":
    t_start = datetime.now()
    signal.signal(signal.SIGINT, signal_handling)
    main()
    print('Total time:', datetime.now() - t_start)
