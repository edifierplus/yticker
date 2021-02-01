import pandas as pd
from tqdm import tqdm
from datetime import datetime

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
        pbar.set_description(f"[Query {queue[idx]}]")
        pbar.refresh()

        try:
            ans, total = ylb.lookup(key=queue[idx], category='all', start=0, size=perpage)
            pbar.write(f"query = {queue[idx]} | count = {len(ans)} | total = {total}")
        except Exception as e:
            pbar.write(f"error: idx = {idx}")
            pbar.write(str(e))
            continue

        if total > perpage:
            add = [queue[idx] + letter for letter in letters]
            queue += add
            pbar.write(f"Add new queries {queue[idx]}[a-z] to queue")
            pbar.reset(total=len(queue))
            pbar.update(n=idx)

        answers.update(ans)
        pbar.update()
        idx += 1

    df = pd.DataFrame(answers)
    df.to_csv('answers.csv')


if __name__ == "__main__":
    t = datetime.now()
    main()
    print(datetime.now() - t)
