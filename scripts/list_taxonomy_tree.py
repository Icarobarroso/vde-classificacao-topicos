import pandas as pd
from src.taxonomy import Taxonomy

tax = Taxonomy('temas.csv')
for disc in ['Penal', 'Processo Penal', 'Direito Penal - Legislação Especial', 'Criminologia']:
    print(f"\n==================== {disc} ====================")
    nodes_disc = [tax.nodes[tid] for tid in tax.active_ids if tax.nodes[tid]['disciplina'] == disc and tax.nodes[tid]['nivel'] == 1]
    for n in sorted(nodes_disc, key=lambda x: x['titulo']):
        filhos = [tax.nodes[c]['titulo'] for c in n['children'] if c in tax.active_ids]
        filhos_str = f" -> Filhos ({len(filhos)}): {', '.join(filhos[:4])}{'...' if len(filhos)>4 else ''}" if filhos else ""
        print(f"[{n['id']}] {n['titulo']}{filhos_str}")
