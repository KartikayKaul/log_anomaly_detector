"""
    DATALOADER
        We just load data randomly using this
""";
import random

def dataloader(n: int,
               templates_list: list[dict],
               normal_prob: float=0.9
               ):
    """
        a generator | lazily generates value from a list of template log values

        PARAMETERS
            n: number of values that will be generated
            templates_list: a list of all the log templates that were generated from generate_data
            normal_prob: probability with which normal logs will be produced
        
        RETURNS
            a generator object
    """

    normal_templates =[t for t in templates_list if t['category'] == 'normal']
    anomaly_templates = [t for t in templates_list if t['category'] == 'anomaly']

    while n>0:
        if random.random() < normal_prob:
            yield random.choice(normal_templates)
        else:
            yield random.choice(anomaly_templates)
        n-=1
        

## DEBUG
if __name__ == "__main__":
    pass