import csv
import numpy as np
import matplotlib.pyplot as plt

running_basic = 'D:\Research\주택모델SIM모델\주택모델-buy0.5\PyMRDEVS_for calibration\MultiThreadWorkingPlace\Combined_Calibration_Results_Random/'

file = open('D:\Research\주택모델SIM모델\주택모델-buy0.5\PyMRDEVS_for calibration\MultiThreadWorkingPlace\HousingMarketSimulation\Validation/real_validation_data_DJ.csv','r')
lines = file.readlines()
titles = lines[0].split(',')[2:]
validation = []
for line in lines[1:]:
    validation.append([float(x) for x in line.split(',')[:-1]])
validation.pop(0)
validation = np.transpose(validation).tolist()
print(validation)
validation_ = []
validation_.append(validation[4][:12])
validation_.append(validation[5][:12])
validation_.append(validation[10][:12])
validation_.append(validation[11][:12])
validation_.append(validation[16][:12])
validation_.append(validation[17][:12])
validation_.append(validation[22][:12])
validation_.append(validation[23][:12])
validation = validation_
print(validation)

def calculateMAPE(sim, val):
    err = []
    for i in range(len(val)):
        e = 0
        for j in range(len(val[0])):
            e += abs(sim[i][j] - val[i][j]) / (val[i][j] * 12.)
        err.append(e)
    e = 0
    for i in range(len(val)):
        e += err[i] / 8.
    err.append(e)
    return err

num = 1
error = []
errors = []
for i in range(num):
    running_folder = running_basic + 'All_Parameter_Experiment_randomSearch_' + str(i)
    err = []
    for j in range(200):
        running_folder = running_basic + 'All_Parameter_Experiment_randomSearch_' + str(i) + '/iteration_' + str(j) + '/'
        file = open(running_folder + 'SimulationResult.csv', 'r')
        lines = file.readlines()
        file.close()
        for k in range(3):
            simResult = []
            for line in lines[8 * k: 8 * (k+1)]:
                line = [float(x) for x in line.split(',')]
                simResult.append(line)
            err.append(calculateMAPE(simResult, validation))

    for k in range(3):
        totError = []
        err_temp = err[200 * k: 200 * (k+1)]
        for i in range(len(err_temp)):
            totError.append(err_temp[i][-1])
        errors.append(totError)
        argmin = np.argmin(totError)
        error.append(err_temp[argmin])

for exp in range(len(errors)):
    min_ = 100
    for j in range(200):
        if errors[exp][j] < min_:
            min_ = errors[exp][j]
        else:
            errors[exp][j] = min_

errors = np.transpose(errors)
mean = []
cov = []
for i in range(len(errors)):
    mean.append(np.mean(errors[i]))
    cov.append(np.sqrt(np.cov(errors[i])))
plt.plot(np.arange(200), mean)
plt.fill_between(np.arange(200), np.subtract(mean, cov), np.add(mean,cov), alpha=0.15)
plt.show()

error = np.transpose(error)
mean = []
cov = []
for i in range(len(error)):
    mean.append(np.mean(error[i]))
    cov.append(np.sqrt(np.cov(error[i])))
print("mean : ", mean)
print("cov : ", cov)