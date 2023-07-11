#Run this cell to open excel files
install.packages("openxlsx")

#Run this cell to open the mblm library tool kit
install.packages("mblm")

library(openxlsx)
library(ggplot2)
##CONFINED DATA
#Read and access the excel file
CO_C<-read.xlsx('Stats Merged and cleaned DNR data 00-23 CO_C and CO_U.xlsx', sheet = "CO_C Max", detectDates = TRUE)

#plotting the data
date=as.Date(CO_C$Sample_Date, format="%yyyy-%mm-%dd") #format dates
plot(CO_C$Sample_Date, CO_C$Measured_Amount, xlab="Year", ylab="Combined Radium (pCi/L)", main="Cambrian-Ordovician Confined", ylim=c(0, 46))
abline(5,0)
legend('topleft', legend = "MCL", col="black", lwd=1.5, bty="n")

#fit a linear model: Gives a p-value to evaluate significance
linearfit<-lm(CO_C$Measured_Amount~CO_C$Sample_Date)
summary(linearfit)
#generates linear fit models. This can help you evaluate the fit of your model
plot(linearfit)
#check assumptions of linear regression. Should be close to zero
sum(linearfit$residuals)
#generates a histogram. Should be normally distributed
hist(linearfit$residuals)
#should be homoscedastic
plot(CO_C$Sample_Date, linearfit$residuals)

#Plotting the linear regression with the dataset:
plot(CO_C$Sample_Date, CO_C$Measured_Amount, xlab="Year", ylab="Combined Radium (pCi/L)", main="Cambrian-Ordovician Confined
     ", ylim=c(0, 46))
lines(CO_C$Sample_Date, linearfit$fitted.values, type='l',col="red")
abline(5,0)
legend('topleft', legend=c("MCL"), col=c("black"), lwd=1.5, bty="n")

#Nonparametric linear regresion - Theil-Sen estimator
#Need at least 35 data points
#null: there is not a statistical linear relationship between x and y
#alternative: there is a statistical linear relationship between x and y
CO_C$dayssince<-as.numeric(difftime(CO_C$Sample_Date,CO_C$Sample_Date[1],units="days"))
CO_C$Amt=as.numeric(CO_C$Measured_Amount)
library(mblm)
ts_model=mblm(Amt~dayssince,CO_C, repeated = FALSE)
#fits Theil-Sen regression
summary(ts_model)
#Plotting the Theil-Sen regression
plot(CO_C$Sample_Date, CO_C$Amt,  main="Cambrian-Ordovician Confined Theil-Sen Regression", xlab="Year", ylab="Combined Radium (pCi/L)", ylim=c(0, 46), col=c("black"), lwd = 1)
lines(CO_C$Sample_Date,ts_model$fitted.values,col="red", lwd=2)
abline(5,0, lwd=1.5)
legend('topleft', legend=c("MCL"), col=c("black"), lwd=2, bty="n")

##UNCONFINED DATA
#Read and access the excel file
CO_U<-read.xlsx('Stats Merged and cleaned DNR data 00-23 CO_C and CO_U.xlsx', sheet = "CO_U Max", detectDates = TRUE)

#plotting the data
date=as.Date(CO_U$Sample_Date, format="%yyyy-%mm-%dd") #format dates
plot(CO_U$Sample_Date, CO_U$Measured_Amount, xlab="Year", ylab="Combined Radium (pCi/L)", main="Cambrian-Ordovician Unconfined", ylim=c(0, 18))
abline(5,0)
legend('topleft', legend = "MCL", col="black", lwd=1.5, bty="n")

#fit a linear model: Gives a p-value to evaluate significance
linearfit<-lm(CO_U$Measured_Amount~CO_U$Sample_Date)
summary(linearfit)
#generates linear fit models. This can help you evaluate the fit of your model
plot(linearfit)
#check assumptions of linear regression. Should be close to zero
sum(linearfit$residuals)
#generates a histogram. Should be normally distributed
hist(linearfit$residuals)
#should be homoscedastic
plot(CO_U$Sample_Date, linearfit$residuals)

#Plotting the linear regression with the dataset:
plot(CO_U$Sample_Date, CO_U$Measured_Amount, xlab="Year", ylab="Combined Radium (pCi/L)", main="Cambrian-Ordovician Unconfined
     ", ylim=c(0, 18))
lines(CO_U$Sample_Date, linearfit$fitted.values, type='l',col="red")
abline(5,0)
legend('topleft', legend=c("MCL"), col=c("black"), lwd=1.5, bty="n")

#Nonparametric linear regresion - Theil-Sen estimator
#Need at least 35 data points
#null: there is not a statistical linear relationship between x and y
#alternative: there is a statistical linear relationship between x and y
CO_U$dayssince<-as.numeric(difftime(CO_U$Sample_Date,CO_U$Sample_Date[1],units="days"))
CO_U$Amt=as.numeric(CO_U$Measured_Amount)
library(mblm)
ts_model=mblm(Amt~dayssince,CO_U, repeated = FALSE)
#fits Theil-Sen regression
summary(ts_model)
#Plotting the Theil-Sen regression
plot(CO_U$Sample_Date, CO_U$Amt,  main="Cambrian-Ordovician Unconfined Theil-Sen Regression", xlab="Year", ylab="Combined Radium (pCi/L)", ylim=c(0, 18), col=c("black"), lwd = 1)
lines(CO_U$Sample_Date,ts_model$fitted.values,col="red", lwd=2)
abline(5,0, lwd=1.5)
legend('topleft', legend=c("MCL"), col=c("black"), lwd=2, bty="n")

