from sklearn.preprocessing import StandardScaler


WEEK_DICT = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
EMPTY = ['', None]


def convert_binary_vector(data_set):
	
	def _one_hot_encoding(len_, idx_):
		encoded = ['0'] * len_
		encoded[idx_] = '1'
		return ','.join(encoded)

	day_of_weeks, times, airs, conditions = [], [], [], [] 
	for i, row in data_set.iterrows():
		# day of week : convert 7 categories to one-hot encoding
		day_of_week = row.day_of_week
		week_idx = WEEK_DICT.index(day_of_week.lower())
		week_len = len(WEEK_DICT)
		week_encoded = _one_hot_encoding(week_len, week_idx)
		day_of_weeks.append(week_encoded)

		# time : convert 24 categories to one-hot encoding
		time_idx = int(row.time)
		time_len = 24
		time_encoded = _one_hot_encoding(time_len, time_idx)	
		times.append(time_encoded)
		
		# air_index : convert 4 categories to one-hot encoding
		if row.air_index not in EMPTY:
			air_idx = int(row.air_index)-1
			air_len = 4
			air_encoded = _one_hot_encoding(air_len, air_idx)
			airs.append(air_encoded)
		else:
			airs.append("")
		
		# condition : convert 4 categories to one-hot encoding
		if row.condition not in EMPTY:
			con_idx = int(row.condition)-1
			con_len = 4
			con_encoded = _one_hot_encoding(con_len, con_idx)	
			conditions.append(con_encoded)	
		else:
			conditions.append("")

	data_set['day_of_week'] = day_of_weeks
	data_set['time'] = times
	data_set['air_index'] = airs
	data_set['condition'] = conditions

	return data_set


SCALER = StandardScaler()
TRAIN_COLS = ['pm10', 'pm25', 'temp', 'rainfall', 'hour_rainfall']


def train_standard_scaling(train_set):
	scaled_data = SCALER.fit_transform(train_set[TRAIN_COLS].astype(float))
	train_set[TRAIN_COLS] = scaled_data
	return train_set


TEST_CASE1_COLS = ['pm10', 'pm25', 'temp', 'rainfall', 'hour_rainfall']
TEST_CASE2_COLS = ['temp', 'rainfall', 'hour_rainfall']


def test_standard_scaling(test_set, case):
	if case == 1:
		test_cols = TEST_CASE1_COLS
	elif case == 2:
		test_cols = TEST_CASE2_COLS
	elif case == 3:
		return test_set
	else:
		raise StopIteration("Error in value of case")
	scaled_data = SCALER.fit_transform(test_set[test_cols].astype(float))
	test_set[test_cols] = scaled_data
	return test_set


