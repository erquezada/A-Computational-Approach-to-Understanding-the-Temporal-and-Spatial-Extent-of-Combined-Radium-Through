# Install packages only if missing
if (!requireNamespace("openxlsx", quietly = TRUE)) {
  install.packages("openxlsx")
}

if (!requireNamespace("mblm", quietly = TRUE)) {
  install.packages("mblm")
}

library(openxlsx)
library(mblm)

# Reusable function for both confined and unconfined data
analyze_radium_data <- function(file_name, sheet_name, plot_title, y_limit) {
  
  # Read Excel sheet
  data <- read.xlsx(file_name, sheet = sheet_name, detectDates = TRUE)
  
  # Make sure Sample_Date is treated as a Date
  data$Sample_Date <- as.Date(data$Sample_Date)
  
  # Make sure Measured_Amount is numeric
  data$Measured_Amount <- as.numeric(data$Measured_Amount)
  
  # Remove rows with missing date or missing measured amount
  data <- data[!is.na(data$Sample_Date) & !is.na(data$Measured_Amount), ]
  
  # Sort data by date
  data <- data[order(data$Sample_Date), ]
  
  # Create numeric time variable for regression
  data$dayssince <- as.numeric(difftime(data$Sample_Date, data$Sample_Date[1], units = "days"))
  data$Amt <- data$Measured_Amount
  
  # -------------------------
  # Basic scatter plot
  # -------------------------
  plot(
    data$Sample_Date,
    data$Measured_Amount,
    xlab = "Year",
    ylab = "Combined Radium (pCi/L)",
    main = plot_title,
    ylim = y_limit,
    pch = 16
  )
  
  abline(h = 5, col = "black", lwd = 1.5)
  legend("topleft", legend = "MCL", col = "black", lwd = 1.5, bty = "n")
  
  # -------------------------
  # Linear regression
  # -------------------------
  linearfit <- lm(Amt ~ dayssince, data = data)
  
  print(summary(linearfit))
  
  # Diagnostic plots
  plot(linearfit)
  
  # Check residual sum
  print(sum(linearfit$residuals))
  
  # Histogram of residuals
  hist(
    linearfit$residuals,
    main = paste(plot_title, "Residual Histogram"),
    xlab = "Residuals"
  )
  
  # Residuals over time
  plot(
    data$Sample_Date,
    linearfit$residuals,
    xlab = "Year",
    ylab = "Residuals",
    main = paste(plot_title, "Residuals Over Time"),
    pch = 16
  )
  
  abline(h = 0, col = "red", lwd = 2)
  
  # Plot linear regression with data
  plot(
    data$Sample_Date,
    data$Measured_Amount,
    xlab = "Year",
    ylab = "Combined Radium (pCi/L)",
    main = paste(plot_title, "Linear Regression"),
    ylim = y_limit,
    pch = 16
  )
  
  lines(
    data$Sample_Date,
    linearfit$fitted.values,
    col = "red",
    lwd = 2
  )
  
  abline(h = 5, col = "black", lwd = 1.5)
  
  legend(
    "topleft",
    legend = c("Linear Regression", "MCL"),
    col = c("red", "black"),
    lwd = c(2, 1.5),
    bty = "n"
  )
  
  # -------------------------
  # Theil-Sen regression
  # -------------------------
  if (nrow(data) >= 35) {
    
    ts_model <- mblm(Amt ~ dayssince, data = data, repeated = FALSE)
    
    print(summary(ts_model))
    
    plot(
      data$Sample_Date,
      data$Amt,
      main = paste(plot_title, "Theil-Sen Regression"),
      xlab = "Year",
      ylab = "Combined Radium (pCi/L)",
      ylim = y_limit,
      col = "black",
      pch = 16
    )
    
    lines(
      data$Sample_Date,
      ts_model$fitted.values,
      col = "red",
      lwd = 2
    )
    
    abline(h = 5, col = "black", lwd = 1.5)
    
    legend(
      "topleft",
      legend = c("Theil-Sen Regression", "MCL"),
      col = c("red", "black"),
      lwd = c(2, 1.5),
      bty = "n"
    )
    
  } else {
    print(paste("Skipping Theil-Sen regression for", plot_title, "- fewer than 35 data points."))
  }
  
  return(data)
}


# File name
file_name <- "Stats Merged and cleaned DNR data 00-23 CO_C and CO_U.xlsx"


# -------------------------
# CONFINED DATA
# -------------------------
CO_C <- analyze_radium_data(
  file_name = file_name,
  sheet_name = "CO_C Max",
  plot_title = "Cambrian-Ordovician Confined",
  y_limit = c(0, 46)
)


# -------------------------
# UNCONFINED DATA
# -------------------------
CO_U <- analyze_radium_data(
  file_name = file_name,
  sheet_name = "CO_U Max",
  plot_title = "Cambrian-Ordovician Unconfined",
  y_limit = c(0, 18)
)