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
        Data generator that 
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