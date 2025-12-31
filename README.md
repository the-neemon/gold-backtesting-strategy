# Gold Backtesting Strategy

A Python-based backtesting engine for testing a multi-leg averaging strategy on gold futures data.

## Overview

This backtesting system simulates a systematic trading strategy that employs multiple entry legs with progressively wider gap triggers. The strategy aims to achieve a 1% profit target while managing risk through position averaging and time-based exit rules.

## Strategy Parameters

- **Lot Sizes**: [6, 4, 6, 6, 6] - Progressive position sizing across 5 legs
- **Gap Percentages**: [0%, 1%, 1.5%, 2%, 2.5%] - Trigger thresholds for each leg
- **Profit Target**: 1% above average entry price
- **Time Limit**: 60 days maximum hold period
- **Gap Ceiling**: 100 points (rounded up)

## Strategy Logic

### Entry Rules

1. **Leg 1**: Executed at the high of the start date
2. **Subsequent Legs (2-5)**: Triggered when price drops below the calculated gap threshold
   - Gap is calculated from both the average price and the previous day's close
   - The lower of the two triggers is used
   - If market gaps down below trigger, execution occurs at open price

### Exit Rules

1. **Profit Target**: Exit when price reaches 1% above average entry price
2. **Time Limit**: Force exit after 60 days
   - If high reaches average price: Exit at no profit/no loss
   - If high below average price: Exit at market close (potential loss)

## Requirements

```
pandas
```

## Data Format

The system expects a CSV file (`data.csv`) with the following columns:

- `date`: Trading date (YYYY-MM-DD format)
- `Open`: Opening price
- `High`: Daily high price
- `Low`: Daily low price
- `Close`: Closing price

Note: Price values may contain commas (e.g., "50,200") and will be automatically cleaned.

## Usage

1. Ensure `data.csv` is in the same directory as `backtest.py`
2. Run the script:
   ```bash
   python backtest.py
   ```
3. Enter the start date when prompted (format: YYYY-MM-DD)

## Output

The system provides:

- Real-time trade log showing each leg execution
- Final cycle summary including:
  - Entry and exit dates
  - Average buy price
  - Exit price
  - Profit or loss amount
- Detailed trade ledger with all transactions

## Example Output

```
--- Simulating Cycle Starting 2021-01-01 ---

CYCLE COMPLETE: TARGET HIT
Entry Date: 2021-01-01
Exit Date:  2021-02-15
Avg Buy Price: 50200.00
Exit Price:    50702.00
PROFIT:        3012.00

--- Trade Ledger ---
Date        Action  Leg    Qty  Price      AvgPrice    Status
2021-01-01  BUY     Leg 1  6    50380.00   50380.00    Started at High
2021-01-15  BUY     Leg 2  4    48655.00   49680.00    Limit Hit
2021-02-15  SELL    Target 10   50702.00   49680.00    Profit Exit
```

## License

This project is provided as-is for educational and research purposes.
