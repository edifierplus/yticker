import time
from datetime import datetime

import pandas as pd
from tqdm import tqdm

import yticker


def main():
    ylb = yticker.YahooLookupBrowser()
    answers = set()

    perpage = 10000
    idx = 0
    letters = list('abcdefghijklmnopqrstuvwxyz')
    queue = list(letters)
    pbar = tqdm(total=len(queue))

    while idx < len(queue):
        pbar.set_description(f"[query = {queue[idx]}]")
        pbar.refresh()

        try:
            t = datetime.now()
            ans, total = ylb.lookup(key=queue[idx], category='all', start=0, size=perpage)
            seconds = (datetime.now() - t).total_seconds()
            pbar.write(f"query = {queue[idx]} | count = {len(ans)} | total = {total} | seconds = {seconds}")
        except Exception as e:
            pbar.write(f"error: idx = {idx}, query = {queue[idx]}. " + str(e))
            pbar.write("wait for 10 seconds...")
            time.sleep(10)  # s
            continue

        if total > perpage:
            add = [queue[idx] + '%20' + letter for letter in letters] + [queue[idx] + letter for letter in letters]
            queue += add
            pbar.write(f"Add new queries {queue[idx]}[%20][a-z] to queue")
            pbar.reset(total=len(queue))
            pbar.update(n=idx)

        answers.update(ans)
        pbar.update()
        idx += 1

    answer_list = sorted(list(answers))
    df = pd.DataFrame(answer_list)
    df.to_csv('answers.csv')


if __name__ == "__main__":
    t_start = datetime.now()
    main()
    print(datetime.now() - t_start)
