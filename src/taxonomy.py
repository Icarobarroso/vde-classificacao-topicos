import pandas as pd
from typing import Dict, Set, List, Optional

class Taxonomy:
    def __init__(self, temas_path: str = "temas.csv"):
        self.df = pd.read_csv(temas_path)
        self.nodes = {}
        self.active_ids = set()
        self.inactive_ids = set()
        
        for _, row in self.df.iterrows():
            tid = int(row['tema_id'])
            pid = int(row['parent_id']) if pd.notna(row['parent_id']) else None
            status = str(row['status']).strip().lower()
            nivel = int(row['nivel'])
            titulo = str(row['titulo']).strip()
            caminho = str(row['caminho']).strip()
            disciplina = str(row['disciplina']).strip()
            descricao = str(row['descricao']).strip() if pd.notna(row['descricao']) else ""
            
            node_data = {
                'id': tid,
                'parent_id': pid,
                'status': status,
                'nivel': nivel,
                'titulo': titulo,
                'caminho': caminho,
                'disciplina': disciplina,
                'descricao': descricao,
                'children': set()
            }
            self.nodes[tid] = node_data
            if status == 'active':
                self.active_ids.add(tid)
            else:
                self.inactive_ids.add(tid)
                
        # Montar filhos
        for tid, data in self.nodes.items():
            pid = data['parent_id']
            if pid is not None and pid in self.nodes:
                self.nodes[pid]['children'].add(tid)

    def get_ancestors(self, tid: int) -> Set[int]:
        ancestors = set()
        curr = self.nodes.get(tid)
        while curr and curr['parent_id'] is not None:
            pid = curr['parent_id']
            ancestors.add(pid)
            curr = self.nodes.get(pid)
        return ancestors

    def get_descendants(self, tid: int) -> Set[int]:
        descendants = set()
        curr = self.nodes.get(tid)
        if not curr:
            return descendants
        queue = list(curr['children'])
        while queue:
            child_id = queue.pop(0)
            descendants.add(child_id)
            child_node = self.nodes.get(child_id)
            if child_node:
                queue.extend(list(child_node['children']))
        return descendants

    def get_valid_branch(self, tid: int) -> Set[int]:
        """
        Retorna o conjunto de IDs válidos para o critério da régua:
        O próprio nó, todos os ancestrais (pais/raízes) e todos os descendentes (filhos/subfilhos).
        """
        if tid not in self.nodes:
            return set()
        return {tid} | self.get_ancestors(tid) | self.get_descendants(tid)

    def is_compatible(self, pred_id: int, target_id: int) -> bool:
        """
        Verifica se pred_id está no mesmo ramo de target_id (ele mesmo, pai ou filho).
        """
        if pred_id == target_id:
            return True
        return pred_id in self.get_valid_branch(target_id)

    def evaluate_prediction(self, pred_decisao: str, pred_tema_id: Optional[int],
                            gold_fora: int, gold_tema_central: Optional[int],
                            gold_extras: List[int]) -> bool:
        """
        Avalia se a predição é correta segundo o edital:
        - Se gold_fora == 1: acerto se pred_decisao == 'fora'.
        - Se gold_fora == 0:
            - Se pred_decisao == 'fora': erro (a questão tinha tema).
            - Se pred_decisao in ('publicar', 'revisar'):
                acerto se pred_tema_id é compatível (mesmo ramo) com gold_tema_central
                ou com qualquer um dos gold_extras.
        """
        if gold_fora == 1:
            return pred_decisao == 'fora'
        
        # Aqui gold_fora == 0
        if pred_decisao == 'fora':
            return False
        
        if pred_tema_id is None:
            return False
            
        # Verificar contra o tema central
        if gold_tema_central is not None and self.is_compatible(pred_tema_id, gold_tema_central):
            return True
            
        # Verificar contra os extras
        for extra_id in gold_extras:
            if self.is_compatible(pred_tema_id, extra_id):
                return True
                
        return False

if __name__ == "__main__":
    tax = Taxonomy()
    print(f"Taxonomia carregada: {len(tax.nodes)} nós ({len(tax.active_ids)} ativos, {len(tax.inactive_ids)} inativos).")
    
    # Testar relações
    # Exemplo: tema 4373 (Escolas Criminológicas) filho de 4371 (Etapas Evolutivas e Escolas)
    print("Ancestrais de 4373:", tax.get_ancestors(4373))
    print("Filhos de 4371:", tax.nodes[4371]['children'])
    print("4371 compatível com 4373?", tax.is_compatible(4371, 4373))
    print("4373 compatível com 4371?", tax.is_compatible(4373, 4371))
