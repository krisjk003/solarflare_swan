# Hardware-Efficient Solar Flare Prediction Using SWAN-SF and FPGA-Based CNN Acceleration

## Project Objective
This project aims to build an end-to-end solar-flare prediction system. It utilizes the SWAN-SF (Space-Weather ANalytics for Solar Flares) multivariate time-series dataset to establish the Cmod CNN as a research baseline. Following the baseline, we will develop our own lightweight CNN suitable for FPGA deployment, evaluating FP32, INT8, and INT7 precisions, before finally deploying the selected model to an FPGA using Vivado.

## Current Project Status
- **Phase 1 (Dataset Research):** Currently investigating the SWAN-SF dataset, establishing the theoretical Cmod baseline, and planning the preprocessing and training pipelines.
- **Phase 2 (Project Code):** Pending dataset and pipeline verification.
- **Phase 3 (FPGA Deployment):** Future step; Vivado/HLS directories will be created after ML pipeline validation.

## Dataset (SWAN-SF)
The Space-Weather ANalytics for Solar Flares (SWAN-SF) is a comprehensive open-access multivariate time-series dataset.
- **Source:** Harvard Dataverse.
- **Structure:** Divided into five chronological partitions (P1–P5) to enable training and testing without temporal leakage. P1–P4 are used for training and validation, while P5 serves as the temporally independent test set.
- **Samples & Features:** Over 4,000 active regions, using 24 magnetic-field parameters derived from SDO/HMI Active Region Patches.
- **Time Resolution:** Observations at 12-minute intervals.
- **Observation Window:** 60 time steps per instance, yielding a 12-hour input/context window.
- **Prediction:** Binary prediction of M/X-class flare occurrence in the following 12 hours.
- **Challenges:** Severe class imbalance (major flares are rare), significant missing data, and temporal redundancy.

## Official Cmod Preprocessing (Replicated)
Based on a deep audit of the official Cmod authors' source code (`foumani/solar_flare_cnn`), we have accurately replicated the exact released preprocessing pipeline:

- **Input Formulation:** Tensor shape is `[N, 24, 60]`. Our PyTorch dataset yields `[N, 60, 24]`, which is seamlessly transposed before input into the Conv1D model.
- **Missing-value Handling:** The paper claims FPCKNN, but the official repository does not contain it. The released implementation uses `local_avg` (a 7-step temporal moving average) followed by a fallback to the batch feature mean.
- **Normalization/Scaling:** The code uses standard Min-Max Scaling (not LSBZM). `X_min` and `X_max` are fitted on the training set.
- **Target Definition:** Binary classification inferred directly from filenames (Q, B, C -> 0; M, X -> 1).
- **Sampling & Imbalance:** The code samples 6500 Negative and 1000 Positive instances using uniform random sampling (`pandas.DataFrame.sample()`). The repository contains a `nonuniform_sample` function, but it is entirely unused in the execution path.
- **NDBSR:** Borderline B and C class flares are explicitly removed from the training set *after* the initial sampling.
- **Validation Split:** Validation data is created by taking a random 50% subset of the shuffled P1-P4 matrix.

### Known Official Leakage Issues
The `OfficialCmodPreprocessor` replicates the official codebase exactly, which unfortunately includes significant data leakage:
1. **Missing Data Leakage:** The fallback average calculation (`nan_to_num`) is computed dynamically on the input batch. This means the Test set imputes values using its own future statistics.
2. **Temporal Validation Leakage:** The random 50% split of the training array causes sequential instances from the same multi-day active region to fall randomly into both Train and Validation sets.

We have structured the codebase to eventually support a `LeakageSafeCmodPreprocessor` to correct these methodological flaws while evaluating the true baseline.

## Cmod Baseline
The Cmod model is a lightweight Convolutional Neural Network (CNN) specifically tailored for multivariate time-series (MVTS) magnetic field data.
- **Architecture:** Lightweight CNN optimized via Bayesian Optimization with HyperBand (BOHB).
- **Target:** Predict ≥ M-class flares within a 12-hour window.
- **Metrics:** True Skill Statistics (TSS), alongside traditional metrics like ROC-AUC, Precision, Recall, and F1-Score.

## Proposed Model (FPGA-Oriented CNN)
Our proposed model will build upon the Cmod baseline but focus heavily on hardware efficiency:
- Configurable input dimensions and class counts.
- Depthwise separable convolutions or standard lightweight Conv1D layers.
- Avoidance of operations that are expensive on FPGAs (e.g., complex activations or massive fully connected layers).
- Quantization-aware design (FP32, INT8, INT7 simulated).

## Training & Evaluation
- **Framework:** PyTorch.
- **Reproducibility:** Strict random seed setting, configurable hyperparameters (in `configs/config.yaml`).
- **Experiment Tracking:** Logging of model version, dataset version, features, seeds, precision, and metrics.
- **Evaluation Metrics:** ROC-AUC, TSS, Precision, Recall, F1, Confusion Matrix, ROC/PR curves.
- **Outputs:** Checkpoints in `checkpoints/`, tables in `results/tables/`, figures in `results/figures/`.

## Quantization
The project will evaluate three precision levels to assess the trade-off between predictive performance and hardware efficiency:
1. **FP32:** Standard PyTorch baseline.
2. **INT8:** Standard PyTorch post-training quantization (PTQ) or quantization-aware training (QAT).
3. **INT7:** Simulated custom quantization. Since PyTorch does not natively support INT7, we will implement a custom hardware-oriented representation and document the approach thoroughly.

## How to Reproduce Experiments
*Instructions will be added once the ML pipeline is implemented and the dataset subset is confirmed.*

## Future FPGA Stage
After the ML pipeline is validated and the INT7 model is selected, the project will transition to FPGA deployment using Vivado HLS.
