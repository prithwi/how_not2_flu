# how_not2_filu
Accompanying material for "how not to forecast flu" paper.


**Table of contents**

1. [Surveillance Instability](#Surveillance-Instability)
1. [Between Surveillance Deviations](#Surveillance-deviations)
2. [Within Surveiillance Deviations](#Strain-deviations)
4. [Drop off of surveillance](#Surveillance-Drop-off)

# Surveillance Instability

Surveillance data is genrally unstable. Usually it takes a number of updates
from the agency before the surveillance data gets stabilizied.  This
instability can vary from one country to another (within a single network) as
well as between networks. Here we analyze the instability of two different kinds
of surveillance networks:

1. [PAHO](#PAHO-Instability): FluNet network for ILI (a lab based system)
2. [CDC](#CDC-Instability): ILINet network for ILI (an outpatient reporting system)

As can be seen both networks show surveillance instability.

## PAHO-Instability


PAHO provides lab based surveillance feeds. We show the phenomenon of
`surveillance drop-off` on this network. PAHO updates for several Latin
American countries were collected daily from `2012-10` to `2013-10`.  ILI
estimates are generally updated at irregular intervals. We assumed the estimate
for a particular country for an epi week as avialable from the last update as
the true value and calculated percentage relative error as:

$\text{Error} = \frac{\text{data} - \text{last_update}}{\text{last_update}}$

The snapshot of the daily downloads can be found in [PAHO
updates](./data/PAHO_2013-10-10.xlsx). We can show the relative error as 
a function of update as given below:
![PAHO Instabiity](./figures/ili_updates.png)

As can be seen in the figure countries fall nicely in two groups as slowly
stabilizing countries  (such as `Colombia` and `Peru`) and quickly stabilizing
countries (such as `Argentina` and `El Salvador`).

## CDC Instability

CDC historical updates for national regions can be accessed from 
[cdc archives](http://www.cdc.gov/flu/weekly/weeklyarchives2013-2014/data/senAllregt09.htm)
(click on the link for an example). A snapshot of the dataset can be 
found in [CDC historical archive snapshot](./data/cdc-historical-2010-2015.csv)

### Animated CDC Updates

An animation of how the CDC updates happens for varios epi weeks is shown
below. We animate the updates for 2013-2014 season for various reporting week
here:
![Animated CDC Updates](./figures/animated_cdc.gif)

### CDC Instability Horizon
Similar to PAHO, we can plot the relative error of updates as a scatter plot as 
shown below. We also plot the mean relative error in this figure.
![CDC instability stats](./figures/cdc_instability.png)

As can be seen, similar to PAHO a number of updates is required before the 
value stabilizies. However, CDC data for USA is found to be `fast stabilizing`. 


- - -


# Surveillance Drop-off

In our opinion piece we posited that, Post-peak the surveillance efforts drops. 
We elucidate this by plotting the
scatter plot of the CDC ILINet reported number of providers as a function of
season week. As the scatter plot shows, the number of providers decreases
sharply at around season week $33$. We identified this point by finding the
inflection point of the averaged and smoothened CDC ILINet number of providers.
The inflection point is also found via smotthened version to account for
sporadic variations. the code snippet for finding the inflection point is given
below. The data archive can be found in [cdc real time
data snapshot](./data/cdc-combined-national-2015-05-25.csv)


```python
selected_cdc = cdc_data.query('season in [2010, 2011, 2012, 2013, 2014]')

# Smoothing data
span_size = 4
avg_providers = selected_cdc.groupby('season_week').agg({'NUM. OF PROVIDERS': 'mean'})
smooth_providers = pd.ewma(avg_providers, span=span_size)

# Calculating gradients on smoothened data
provider_summary = pd.DataFrame(index=smooth_providers.index)
provider_summary['average'] = smooth_providers
provider_summary['grad2'] = np.gradient(np.gradient(smooth_providers.values.flatten()))
provider_summary['grad2sign'] = np.sign(provider_summary['grad2'])

# Calculating smoothened inflection point
provider_summary['inflect'] =  pd.rolling_sum(provider_summary['grad2sign'], 
                                              window=span_size).shift(-span_size + 1)

# Inflection point = first point where you get a sum of span_size
inflection_point = provider_summary[provider_summary['inflect'] == span_size].index[0]
```

The resultant scatter plot is shown below:

![CDC Scatter plot](./figures/ili_surveillance_drop.png)


# Surveillance Deviations 

Often times, there are deviations in estimated ILI incidence for two different
networks for the same region. We illustrate this for CDC by comparing `ILINet` 
against `WHO NREVSS`. We show this comparison for the national region. However, 
similar analysis can be done for other regions as well. We compare the
estimates from two different networks below:
The data archive can be found in [cdc
real time data snapshot](./data/cdc-combined-national-2015-05-25.csv)

![ILINet vs WHO NREVSS](./figures/ilinet_vs_nrevss.png)



# Strain Deviations

Similar to surveillane deviations, there could be deviations in ILI patterns
for different strains that is broadly encompassed by the term ILI. 

Strain estimates can be obtained from `WHO NREVSS` (which is a lab based
surveillance system). We scale the strain estimates to ILINet reported levels
and compare the incidence of total ILI vs Flu A and Flu B. 

The code snippet for the scale conversions is given below:

```python
# **************************************************************
#                   MANIPULATORS
# **************************************************************
# Get ratios
def get_ratios(X, col1='FLUA', col2='B', epsilon=1, suffix='_per'):
    """ lambda funtion to get ratios of col1 and col2 as percentage.
    """
    denom = X[col1] + X[col2] + epsilon
    num1 = ((X[col1] + epsilon)/ denom).fillna(0)
    num2 = ((X[col2] + epsilon)/ denom).fillna(0)
    return pd.DataFrame({col1+suffix: num1,
                         col2+suffix: num2})


# Get ILINET values
def get_values(X):
    """ lambda funtion to get ILINET VALUES
    """
    
    return (np.round(X['FLUA_per'] * X['ILITOTAL']),
            np.round(X['B_per'] * X['ILITOTAL']))


# ***************************************************************
#                   Scaling of WHO data to ILINet Scale
# ***************************************************************
combined_who_columns = [u'PERCENT POSITIVE', u'B',
                        u'FLUA', u'FLUA_per', u'B_per']
# calculating ratios of strains
cdc_who[['FLUA_per', 'B_per']] = (get_ratios(cdc_who, epsilon=0)
                                  [['FLUA_per', 'B_per']])
# merging frames
combined_df = (cdc_net.join(cdc_who[combined_who_columns]))['2004':]
# Scaling ILINet according to strain ratios
combined_df['ILI_FLUA'], combined_df['ILI_FLUB'] = zip(*combined_df.apply(get_values, axis=1)) 
```
The raw [ILINet data](./data/cdc-ILINet-national-2015-05-25.csv) and 
[NREVSS data](./data/cdc-WHO_NREVSS-national-2015-05-25.csv) is merged 
together to [Combined data](./data/cdc-combined-national-2015-05-25.csv) 
for pulbic perusal.

This can be show pictorially as given below which shows a phase deviation
between Flu B and ILI
![CDC ILI strain offsets](./figures/ilinet_subtyped.png)
