import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import pickle

# --- 1. Synthetic Time Series Dataset Generation for Cycling ---

def calories_hr(row):
    HR = row['heart_rate']
    weight_lbs = row['weight_lbs']
    # Convert lb weight to kg
    weight_kg = weight_lbs * 0.453592

    # calculate the start time of the ride fort eh lap number form the df and calculate the current suration using the currnt timestamp
    
    
    age = row['age']
    
    if row['sex'] == 'Female':
        kcal_min = (-20.4022 + 0.4472*HR - 0.1263*weight_kg + 0.074*age) / 4.184
    else: # Male
        kcal_min = (-55.0969 + 0.6309*HR + 0.1988*weight_kg + 0.2017*age) / 4.184
    
    # Convert to calories for the current timestep
    return kcal_min * (row['duration_sec'] / 60.0)




def calories_power(row):
    watts = row['power']
    duration = row['duration_sec']
    
    # human mechanical efficiency ~24%
    kcal = (watts * duration) / (0.24 * 4184)
    return kcal

def calculate_duration_from_lap_start(df):
    """
    Calculate duration in seconds from the start of each lap for every record.
    Handles mixed datetime formats and missing values - without nested functions.
    """
    df = df.copy()
    
    # Ensure timestamp is datetime - handle mixed formats
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', errors='coerce', utc=True)
    except:
        # Fallback for older pandas versions
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', infer_datetime_format=True, utc=True)
    
    # Remove rows with invalid timestamps
    initial_count = len(df)
    df = df.dropna(subset=['timestamp'])
    if len(df) < initial_count:
        print(f"Warning: Removed {initial_count - len(df)} rows with invalid timestamps")
    
    # Sort by lap and timestamp to ensure proper chronological order
    df = df.sort_values(['lap', 'timestamp']).reset_index(drop=True)
    
    # Calculate start time for each lap
    lap_start_times = df.groupby('lap')['timestamp'].min()
    
    # Map start times back to each record and calculate duration
    df['lap_start_time'] = df['lap'].map(lap_start_times)
    df['duration_sec'] = (df['timestamp'] - df['lap_start_time']).dt.seconds
    
    # Drop the temporary column
    df = df.drop('lap_start_time', axis=1)
    
    return df

def generate_cycling_data(route_distance_km=40, sample_rate_sec=5,weight_lbs = 150, age = 30, sex = 0, height = 5.9):
    """
    Generates a synthetic time series dataset for a cycling ride,
    including Time, Distance, Elevation, Power, and Heart Rate.
    
    The Power and HR are calculated based on the simulated Elevation profile.
    """
    
    total_seconds = int((route_distance_km / 25) * 3600)  # Assume avg speed 25 km/h for estimation
    n_steps = total_seconds // sample_rate_sec
    time_index = pd.to_datetime('2024-01-01 09:00:00') + pd.to_timedelta(np.arange(n_steps) * sample_rate_sec, unit='s')
    
    # --- Feature Generation ---
    
    # 1. Distance (Monotonically increasing)
    distance_km = np.linspace(0, route_distance_km, n_steps)
    
    # 2. Elevation Profile (Simulated Route)
    # Start flat, climb a hill, flat plateau, descent, finish flat.
    elevation = np.zeros(n_steps)
    
    # Section 1: 0-10km (Rolling hills/Flat)
    segment_1_end = int(0.25 * n_steps)
    elevation[:segment_1_end] = np.random.normal(0, 1, segment_1_end).cumsum() + 100
    
    # Section 2: 10-25km (Major Climb)
    segment_2_start = segment_1_end
    segment_2_end = int(0.6 * n_steps)
    climb_slope = np.linspace(0, 300, segment_2_end - segment_2_start)
    elevation[segment_2_start:segment_2_end] = elevation[segment_2_start-1] + climb_slope
    
    # Section 3: 25-35km (Descent and Finish)
    segment_3_start = segment_2_end
    descent_slope = np.linspace(0, -250, n_steps - segment_3_start)
    elevation[segment_3_start:] = elevation[segment_3_start-1] + descent_slope
    
    # Smooth and clean up elevation to avoid sharp drops below start altitude
    elevation = np.maximum(elevation, 100) # Ensure a minimum starting altitude
    elevation = pd.Series(elevation).rolling(window=10, min_periods=1).mean().values
    
    # Calculate Rate of Climb (Gradient Proxy)
    elevation_diff = np.diff(elevation, prepend=elevation[0])
    
    # --- Target Variable Generation (Power & HR) ---
    
    # 3. Power Output (Watts)
    base_power = 180 # Base steady-state power
    
    # Power is highly dependent on positive elevation change (climbing effort)
    # Power = Base + (Elevation_Change * Factor) + Noise
    power = base_power + (elevation_diff * 40) + np.random.normal(0, 15, n_steps)
    
    # Minimum power is 0 (coasting)
    power = np.maximum(power, 0)
    
    # 4. Heart Rate (BPM)
    base_hr = 120 # Base Heart Rate
    max_hr = 180 # Cap
    
    # HR is proportional to Power, but with a lag (it takes time for the body to react)
    hr_raw = base_hr + (power * 0.15) 
    
    # Apply a rolling average to simulate physiological lag (30-second window)
    lag_window = 30 // sample_rate_sec
    hr_lagged = pd.Series(hr_raw).rolling(window=lag_window, min_periods=1).mean()
    
    # Add noise and apply limits
    heart_rate = (hr_lagged + np.random.normal(0, 3, n_steps)).clip(lower=base_hr, upper=max_hr).round(0).astype(int)
    
    # calculate speed in miles per hour based on the power and weight of the rider and heart rate
    speed = (power / (weight_lbs * 0.453592)) * 2.5 + np.random.normal(0, 1, n_steps)
    speed = np.clip(speed, 5, 30).round(1)

    # calculate cadence as a function of power and speed
    cadence = (power / 2) + np.random.normal(0, 5, n_steps)
    cadence = np.clip(cadence, 50, 120).round(0).astype(int)




    df = pd.DataFrame({
        'timestamp': time_index,
        'Distance_km': distance_km.round(2),
        'Elevation_m': elevation.round(1),
        'power': power.round(0).astype(int),
        'heart_rate': heart_rate,
        'cadence': cadence,
        'speed': speed
    })
    df['age'] = np.repeat(age, len(df))
    df['weight_lbs'] = np.repeat(weight_lbs, len(df))
    df['weight_kg'] = df['weight_lbs'] * 0.453592
    df['sex'] = np.repeat(sex, len(df))
    df['height'] = np.repeat(height, len(df))
    df['lap'] = np.repeat(1, len(df))
    df_with_duration = calculate_duration_from_lap_start(df)

    df_with_duration['calories_hr'] = df_with_duration.apply(calories_hr, axis=1)

    df_with_duration['calories_power'] = df_with_duration.apply(calories_power, axis=1)
    df_with_duration['calories_total'] = 0.7*df_with_duration['calories_hr'] + 0.3*df_with_duration['calories_power']



    # df_with_duration.set_index('timestamp', inplace=True)
    print(f"--- Generated Synthetic Cycling Data ({route_distance_km}km Ride) ---")
    print(df_with_duration.head())
    return df_with_duration

def make_realtime_prediction(model, test_data):
    """
    Makes predictions on a test dataset using the trained OLS model.
    """
    
    features = [
         'heart_rate', 'cadence', 'speed', 'power', 'lap', 'age',
       'sex', 'height', 'weight_lbs', 'weight_kg', 'duration_sec',
       'calories_hr', 'calories_power'
    ]
    # Ensure test data has required features and handle NaNs
    X_test = test_data[features].fillna(test_data[features].mean())
    # X_test = sm.add_constant(X_test, has_constant='add')
    
    # Prediction
    predicted_burn = model.predict(X_test).round(2)
    
    print("\n--- TEST DATA PREDICTION SAMPLE ---")
    prediction_df = pd.DataFrame({
        'Test_Time': test_data.timestamp,
        'Predicted_Kcal_Burn': predicted_burn,
        'calculated_power_kcal': test_data['calories_total'],
    }).set_index('Test_Time')
    
    print(prediction_df.head(10))
    
    return prediction_df, predicted_burn

if __name__ == '__main__':
    # 1. Generate the dummy data for a 40km ride (Source of truth)
    df_test = generate_cycling_data(route_distance_km=40, sample_rate_sec=5, weight_lbs=150, age=30, sex=0, height=5.9)

    with open('cal_burn_model.pkl', 'rb') as f:
        cal_burn_model = pickle.load(f)
    
    prediction_df, predicted_burn = make_realtime_prediction(cal_burn_model, df_test)

    with open('predicted_calorie_burn_test01.csv', 'w') as f:
        prediction_df.to_csv(f)

    # 2. Plot Predicted vs Calculated Kcal Burn
    plt.figure(figsize=(10, 8))
    plt.scatter(prediction_df['Predicted_Kcal_Burn'], prediction_df['calculated_power_kcal'], marker='o', color='#3b82f6', linestyle='None', edgecolor='k', alpha=0.7)
    plt.xlabel('Predicted Kcal Burn (XGBoost Model)')
    plt.ylabel('Calculated Kcal Burn (Power-Based)')
    plt.title('XGB Predicted vs Calculated Kcal Burn')
    plt.grid(True)
    plt.show()
