from nfce import nf_gov_para_csv
import sys
    
if __name__ == '__main__':
    
    if  len(sys.argv) == 2:
        pasta = sys.argv[1]
        nf_gov_para_csv(pasta)
    else:
        print(len(sys.argv))
        print('Comando inválido. Forma correta de uso: nf_gov_csv.py <caminho para pasta onde estão as notas fiscais')
