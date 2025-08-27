
# Machine Learning Project Checklist

This checklist can guide you through your machine learning projects. There are eight main steps:

1. **Frame the problem and look at the big picture.**  
2. **Get the data.**  
3. **Explore the data to gain insights.**  
4. **Prepare the data to better expose the underlying data patterns to machine learning algorithms.**  
5. **Explore many different models and shortlist the best ones.**  
6. **Fine-tune your models and combine them into a great solution.**  
7. **Present your solution.**  
8. **Launch, monitor, and maintain your system.**  

*Obviously, you should feel free to adapt this checklist to your needs. In other words it depends on what you are trying to do*

Adopted from: Hands-On Machine Learning by Aurélien Géron

---

## 1. Frame the Problem and Look at the Big Picture

1. Define the objective in business terms.  
2. How will your solution be used?  
3. What are the current solutions/workarounds (if any)?  
4. How should you frame this problem (supervised/unsupervised, online/offline, etc.)?  
5. How should performance be measured?  
6. Is the performance measure aligned with the business objective?  
7. What would be the minimum performance needed to reach the business objective?  
8. What are comparable problems? Can you reuse experience or tools?  
9. Is human expertise available?  
10. How would you solve the problem manually?  
11. List the assumptions you (or others) have made so far.  
12. Verify assumptions if possible.

---

## 2. Get the Data

*Note: automate as much as possible so you can easily get fresh data.*

1. List the data you need and how much you need.  
2. Find and document where you can get that data.  
3. Check how much space it will take.  
4. Check legal obligations, and get authorization if necessary.  
5. Get access authorizations.  
6. Create a workspace (with enough storage space).  
7. Get the data.  
8. Convert the data to a format you can easily manipulate (without changing the data itself).  
9. Ensure sensitive information is deleted or protected (e.g., anonymized).  
10. Check the size and type of data (time series, sample, geographical, etc.).  
11. Sample a test set, put it aside, and never look at it (no data snooping!).

---

## 3. Explore the Data

*Note: try to get insights from a field expert for these steps.*

1. Create a copy of the data for exploration (sampling it down to a manageable size if necessary).  
2. Create a Jupyter notebook to keep a record of your data exploration.  
3. Study each attribute and its characteristics:  
   - Name  
   - Type (categorical, int/float, bounded/unbounded, text, structured, etc.)  
   - % of missing values  
   - Noisiness and type of noise (e.g., outliers, rounding errors)  
   - Usefulness for the task  
   - Type of distribution (Gaussian, uniform, logarithmic, etc.)  
4. For supervised learning tasks, identify the target attribute(s).  
5. Visualize the data.  
6. Study the correlations between attributes.  
7. Study how you would solve the problem manually.  
8. Identify the promising transformations you may want to apply.  
9. Identify extra data that would be useful (go back to “Get the Data”).  
10. Document what you have learned.

---

## 4. Prepare the Data

*Notes: Work on copies of the data. Write functions for all transformations for reusability and traceability.*

1. **Clean the data:**  
   - Fix or remove outliers (optional).  
   - Fill in missing values (e.g., with zero, mean, median…) or drop their rows/columns.  

2. **Perform feature selection (optional):**  
   - Drop attributes that provide no useful information.  

3. **Perform feature engineering (where appropriate):**  
   - Discretize continuous features.  
   - Decompose features (e.g., categorical, date/time).  
   - Add promising transformations (e.g., log(x), sqrt(x)).  
   - Aggregate features into new features.  

4. **Perform feature scaling:**  
   - Standardize or normalize features.

---

## 5. Shortlist Promising Models

*Notes: For large datasets, consider smaller training sets for quick experimentation.*

1. Train many models from different families (e.g., linear, SVM, decision trees, neural nets).  
2. Measure and compare performance (e.g., using N-fold cross-validation).  
3. Analyze significant variables for each algorithm.  
4. Analyze types of errors and what humans would use to avoid them.  
5. Quick round of feature selection/engineering.  
6. Iterate the above steps a few times.  
7. Shortlist 3–5 models that perform well and make different types of errors.

---

## 6. Fine-Tune the System

*Use as much data as possible. Automate when feasible.*

1. Fine-tune hyperparameters using cross-validation:  
   - Treat data prep choices as hyperparameters.  
   - Prefer random search over grid search. Consider Bayesian optimization for long training.  

2. Try ensemble methods.  
3. Evaluate final model on the test set to estimate generalization error.  

⚠️ **Warning**: Don’t tweak the model after evaluating on the test set to avoid overfitting.

---

## 7. Present Your Solution

1. Document your process and findings.  
2. Create a clear, structured presentation:  
   - Start with the big picture  
   - Explain how your solution meets the business objective  
3. Present interesting findings and challenges.  
4. List assumptions and limitations.  
5. Highlight key insights with strong visuals or memorable summaries.

---

## 8. Launch!

1. Prepare the system for production (e.g., plug into data pipelines, add unit tests).  
2. Write monitoring tools:  
   - Detect performance degradation over time  
   - Use human evaluation if necessary  
   - Monitor input data quality  

3. Automate retraining on fresh data.
