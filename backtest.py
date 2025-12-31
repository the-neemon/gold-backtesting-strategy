import pandas as pd
import math

# ==========================================
# 1. SETUP & PARAMETERS
# ==========================================

file_path = 'data.csv'

# Strategy Parameters
LOT_SIZES = [6, 4, 6, 6, 6]  
GAPS = [0, 0.01, 0.015, 0.02, 0.025] 

def clean_numeric(val):
    if isinstance(val, str):
        return float(val.replace(',', ''))
    return float(val)

def get_ceiled_gap(price, percentage):
    gap_val = price * percentage
    return math.ceil(gap_val / 100) * 100

# ==========================================
# 2. LOAD DATA
# ==========================================

try:
    df = pd.read_csv(file_path)
    cols_to_clean = ['Open', 'High', 'Low', 'Close']
    for col in cols_to_clean:
        df[col] = df[col].apply(clean_numeric)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# ==========================================
# 3. USER INPUT
# ==========================================

print(f"\nData available from {df['date'].min().date()} to {df['date'].max().date()}")
user_date = input("Enter Start Date for this Cycle (YYYY-MM-DD): ")

try:
    start_date_obj = pd.to_datetime(user_date)
    subset = df[df['date'] >= start_date_obj].reset_index(drop=True)
    if subset.empty:
        print("No data found after this date.")
        exit()
except ValueError:
    print("Invalid date format.")
    exit()

# ==========================================
# 4. SINGLE CYCLE ENGINE (CORRECTED)
# ==========================================

position_open = False
current_leg = 0
total_lots = 0
total_cost = 0
avg_price = 0
last_buy_day_close = 0
entry_date = None
cycle_ledger = []

print(f"\n--- Simulating Cycle Starting {subset.iloc[0]['date'].date()} ---")

for i, row in subset.iterrows():
    date = row['date']
    high = row['High']
    low = row['Low']
    close = row['Close']
    open_p = row['Open']

    # --- START LEG 1 (Buy at High of Start Date) ---
    if not position_open:
        if i == 0:
            current_leg = 0
            qty = LOT_SIZES[current_leg]
            
            # Leg 1 Rule: Buy at Day's High
            buy_price = high
            
            total_lots = qty
            total_cost = qty * buy_price
            avg_price = buy_price
            last_buy_day_close = close
            entry_date = date
            position_open = True
            
            cycle_ledger.append([date.date(), 'BUY', f'Leg {current_leg+1}', qty, buy_price, f"{avg_price:.2f}", "Started at High"])
        continue

    # --- MANAGE ACTIVE POSITION ---
    
    # 1. Check Profit Target
    target_exit = avg_price * 1.01
    
    if high >= target_exit:
        exit_price = target_exit
        profit = (exit_price - avg_price) * total_lots
        cycle_ledger.append([date.date(), 'SELL', 'Target', total_lots, exit_price, f"{avg_price:.2f}", "Profit Exit"])
        
        print("\n✅ CYCLE COMPLETE: TARGET HIT")
        print(f"Entry Date: {entry_date.date()}")
        print(f"Exit Date:  {date.date()}")
        print(f"Avg Buy Price: {avg_price:.2f}")
        print(f"Exit Price:    {exit_price:.2f}")
        print(f"PROFIT:        {profit:.2f}")
        break 

    # 2. Check Time Limit (60 Days)
    if (date - entry_date).days >= 60:
        
        # REALISTIC EXIT LOGIC:
        # If High >= AvgPrice, we could have exited at NPNL.
        # If High < AvgPrice, we must exit at Market Close (Loss).
        
        if high >= avg_price:
            exit_price = avg_price
            status = "Time Exit (NPNL)"
        else:
            exit_price = close # Forced exit at market close
            status = "Time Exit (Loss)"
            
        profit_loss = (exit_price - avg_price) * total_lots
        cycle_ledger.append([date.date(), 'SELL', 'TimeLimit', total_lots, exit_price, f"{avg_price:.2f}", status])
        
        print(f"\n⚠️ CYCLE COMPLETE: {status}")
        print(f"Entry Date: {entry_date.date()}")
        print(f"Exit Date:  {date.date()}")
        print(f"Avg Buy Price: {avg_price:.2f}")
        print(f"Exit Price:    {exit_price:.2f}")
        print(f"PROFIT/LOSS:   {profit_loss:.2f}")
        break 

    # 3. Check Next Leg Entry (With Gap Down Logic)
    if current_leg < 4:
        next_leg_idx = current_leg + 1
        gap_pct = GAPS[next_leg_idx]
        
        gap_from_avg = get_ceiled_gap(avg_price, gap_pct)
        gap_from_close = get_ceiled_gap(last_buy_day_close, gap_pct)
        
        trigger_price = min(avg_price - gap_from_avg, last_buy_day_close - gap_from_close)
        
        # Check if Low hit the trigger
        if low <= trigger_price:
            
            # GAP DOWN LOGIC:
            # If the market opened BELOW our trigger, we get filled at Open (Better Price).
            # If the market opened ABOVE our trigger but dropped, we get filled at Trigger.
            if open_p < trigger_price:
                buy_price = open_p
                note = "Gap Down Entry"
            else:
                buy_price = trigger_price
                note = "Limit Hit"
                
            qty = LOT_SIZES[next_leg_idx]
            
            total_cost += qty * buy_price
            total_lots += qty
            avg_price = total_cost / total_lots
            last_buy_day_close = close
            current_leg += 1
            
            cycle_ledger.append([date.date(), 'BUY', f'Leg {current_leg+1}', qty, buy_price, f"{avg_price:.2f}", note])

# Print Ledger
print("\n--- Trade Ledger ---")
ledger_df = pd.DataFrame(cycle_ledger, columns=['Date', 'Action', 'Leg', 'Qty', 'Price', 'AvgPrice', 'Status'])
print(ledger_df.to_string(index=False))