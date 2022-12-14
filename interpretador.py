'''
AUTORES: FABIO SEITI FUKUDA
         PEDRO AUGUSTO TORTOLA PEREIRA
'''

from copy import deepcopy
from tabela import Tabela

class Interpretador:
    def __init__(self):
        self.interpretacaoSelect = None
        self.interpretacaoFrom = None
        self.interpretacaoWhere = None
        self.interpretacaoOrderBy = None

    def interpretar(self,comando:str):
        comandosSeparados = self.sanitizaComando(comando)
        select_,from_,where_,orderBy_ = self.classificaComandos(comandosSeparados)

        self.interpretacaoSelect = self.interpretarSelect(select_)
        self.interpretacaoFrom = self.interpretarFrom(from_)
        self.interpretacaoWhere = self.interpretarWhere(where_)
        self.interpretacaoOrderBy = self.interpretarOrderBy(orderBy_)

    def interpretarOrderBy(self,orderBy_):
        if len(orderBy_) == 0:
            return None

        nome = ''
        tabela = ''
        direcao = ''

        if '.' in orderBy_[0]:
            tabela,nome = orderBy_[0].split('.')
        else:
            nome = orderBy_[0]
        
        if len(orderBy_)>1:
            direcao = orderBy_[1]
        else:
            direcao = 'asc'

        interpretacaoOrderBy = {
            'nome': nome,
            'tabela': tabela,
            'direcao': direcao.lower()
        }

        return interpretacaoOrderBy
        
    def interpretarWhere(self,where_):
        if len(where_) == 0:
            return None
            
        '''
        where n.idade >= 3

        >	Maior que
        >=	Maior ou igual
        <	Menor que
        <=	Menor ou igual
        <> ou !=	Diferente de
        =	Igual

        LIKE	Busca um padrão parecido

        ''' 

        interpretacaoWhere = []
        where = []
        #Verifica se a condicao do where está contatenada (ex: idade>=4, ao invés de idade >= 4)
        for filtro in where_:
            if len(filtro)<3 and filtro!='and' and filtro!='or':
                novo_filtro = []
                for operacao in filtro:
                    if len(operacao) >=2:
                        flag = False
                        #Tenta encontrar os operadores <= e >= nos operadores
                        for operador in ['>=','<=','<>','!=']:
                            if(flag):
                                break
                            if operador in operacao:
                                flag = True
                                index = operacao.find(operador)
                                valor1 = '' 
                                op = ''
                                valor2 = '' 
                                # idade>= (operador grudado no primeiro valor)
                                if index !=0:
                                    valor1 = operacao[:index]
                                    op = operacao[index:index+2]
                                    # O segundo valor também está grudado (ex:idade>=4)
                                    novo_filtro.append(valor1)
                                    novo_filtro.append(op)
                                    if len(operacao) != index+2:
                                        valor2 = operacao[index+2:]
                                        novo_filtro.append(valor2)
                                # Se o tamanho da operacao é maior que 2, e o primeiro valor não está grudado,
                                #então o segundo valor está grudado.
                                else:
                                    op = operacao[index:index+2]
                                    valor2 = operacao[index+2:]
                                    novo_filtro.append(op)
                                    novo_filtro.append(valor2)
                        for operador in ['>','<','=']:
                            if(flag):
                                break
                            if operador in operacao:
                                flag = True
                                index = operacao.find(operador)
                                valor1 = '' 
                                op = ''
                                valor2 = '' 
                                # idade>= (operador grudado no primeiro valor)
                                if index !=0:
                                    valor1 = operacao[:index]
                                    op = operacao[index:index+1]
                                    novo_filtro.append(valor1)
                                    novo_filtro.append(op)
                                    # O segundo valor também está grudado (ex:idade>=4)
                                    if len(operacao) != index+1:
                                        valor2 = operacao[index+1:]
                                        novo_filtro.append(valor2)
                                # Se o tamanho da operacao é maior que 2, e o primeiro valor não está grudado,
                                #então o segundo valor está grudado.
                                else:
                                    op = operacao[index:index+1]
                                    valor2 = operacao[index+1:]
                                    novo_filtro.append(op)
                                    novo_filtro.append(valor2)
                        if not flag:
                            novo_filtro.append(operacao)
                    else:
                        novo_filtro.append(operacao)
                where.append(novo_filtro)
            else:
                where.append(filtro)
        where_ = where
        '''
                >	Maior que
                >=	Maior ou igual
                <	Menor que
                <=	Menor ou igual
                <> ou !=	Diferente de
                =	Igual
            '''
        
        for operacao in where_:
            if operacao == 'and' or operacao == 'or':
                interpretacaoWhere.append(operacao)
                continue

            valor1 = ''
            tabela1  = ''
            valor2 = ''
            tabela2  = ''
            op = ''

            if operacao[0].isnumeric():
                float(operacao[0])
                tabela1 = "NUMERO"
                valor1 = operacao[0]
            else: 
                if '.' in operacao[0]:
                    tabela1,valor1 = operacao[0].split('.')
                elif operacao[0].find("'")!=-1 or operacao[0].find('"')!=-1:
                    tabela1 = "STRING"
                    valor1 = operacao[0][1:-1]
                else:
                    tabela1 = ""
                    valor1 = operacao[0] 
            if operacao[2].isnumeric():
                float(operacao[2])
                tabela2 = "NUMERO"
                valor2 = operacao[2]
            else: 
                if '.' in operacao[2]:
                    tabela2,valor2 = operacao[2].split('.')
                elif operacao[2].find("'")!=-1 or operacao[2].find('"')!=-1:
                    tabela2 = "STRING"
                    valor2 = operacao[2][1:-1]
                else:
                    tabela2 = ""
                    valor2 = operacao[2]  
            op = operacao[1]

            interpretacaoWhere.append({
                'valor1':valor1,
                'valor2':valor2,
                'tabela1':tabela1,
                'tabela2':tabela2,
                'operacao':op
            })

        for operacao in interpretacaoWhere:
            if isinstance(operacao, dict):
                aliasTabela1 = operacao['tabela1']
                campo1EhValor = False

                if  aliasTabela1 != '' and aliasTabela1=='STRING' or aliasTabela1=='NUMERO': 
                    campo1EhValor = True

                aliasTabela2 = operacao['tabela2']
                campo2EhValor = False

                if aliasTabela2 != '' and aliasTabela2=='STRING' or aliasTabela2=='NUMERO': 
                    campo2EhValor = True

                if not campo1EhValor and campo2EhValor:
                    operacao['join'] = False
                elif not campo2EhValor and campo1EhValor:
                    operacao['valor1'],operacao['valor2'] = operacao['valor2'],operacao['valor1']
                    operacao['tabela1'],operacao['tabela2'] = operacao['tabela2'],operacao['tabela1']
                    operacao['join'] = False
                elif not campo1EhValor and not campo1EhValor:
                    operacao['join'] = True
                else:  
                    operacao['join'] = True              
                    break
                    
        return interpretacaoWhere

    def interpretarSelect(self,select_):
        interpretacaoSelect = {'nome':[],
                        'alias':[],
                        'tabela':[]}
        
        camposSeparados = []
        campo = []
        for comando in select_:
            if comando == ',':
                camposSeparados.append(campo)
                campo = []
            else:
                campo.append(comando)
        camposSeparados.append(campo)

        for campo in camposSeparados:
            proximoCampo = 'nome'
            nome = ''
            alias = ''
            tabela = ''
            for comando in campo:
                if proximoCampo == 'nome':
                    if '.' in comando:
                        tabela,nome = comando.split('.')
                    else:
                        nome = comando
                    proximoCampo = 'alias'
                    continue
                if comando == 'as':
                    continue
                elif proximoCampo == 'alias':
                    alias = comando
            if alias == '':
                alias = nome
            interpretacaoSelect['alias'].append(alias)     
            interpretacaoSelect['nome'].append(nome)
            interpretacaoSelect['tabela'].append(tabela)

        return interpretacaoSelect

    def interpretarFrom(self,from_):
        interpretacaoFrom = {'tabela':[],
                        'alias':[],
                        'joinEn':False,
                        'join':{'tabela':[],'att':[],'op':[]},
                        'usingEn':False,
                        'using':{'campo':[]}}
        
        camposSeparados = []

        for comando in from_:
            if comando == ',':
                continue
            else:
                camposSeparados.append(comando)

        relacao = []
        proximoCampo = 'tabela'
        for campo in camposSeparados:
            index = campo.find("using")
            tabela = ''
            alias = ''
        
            if campo == 'inner' or campo == 'join':
                proximoCampo = 'tabela' 
                interpretacaoFrom['joinEn'] = True
                continue
            elif campo == 'on':
                proximoCampo = 'relacao'
                continue
            elif index!=-1:
                interpretacaoFrom['usingEn'] = True
                indexParenteses1 = campo.find('(')
                if(indexParenteses1 == len(campo)-1):
                    proximoCampo = 'using'
                    continue
                else:
                    proximoCampo = 'nulo'
                    indexParenteses2 = campo.find(')')
                    if(indexParenteses2 != -1):
                        interpretacaoFrom['using']['campo'] = campo[indexParenteses1+1:indexParenteses2]
                    else:
                        interpretacaoFrom['using']['campo'] = campo[indexParenteses1+1:]
            elif campo == ')':
                continue
            elif campo == '':
                continue
            if(proximoCampo == 'using'):
                indexParenteses2 = campo.find(')')
                if(indexParenteses2 != -1):
                    interpretacaoFrom['using']['campo'] = campo[:indexParenteses2]
                else:
                    interpretacaoFrom['using']['campo'] = campo

            if proximoCampo == 'tabela':
                interpretacaoFrom['tabela'].append(campo)
                interpretacaoFrom['alias'].append(campo) 
                continue
            if proximoCampo == 'relacao':
                relacao.append(campo)

        relacao_ = []
        for operacao in relacao:
            if len(operacao) >=2:
                flag = False
                #Tenta encontrar os operadores <= e >= nos operadores
                for operador in ['>=','<=','<>','!=']:
                    if(flag):
                        break
                    if operador in operacao:
                        flag = True
                        index = operacao.find(operador)
                        valor1 = '' 
                        op = ''
                        valor2 = '' 
                        # idade>= (operador grudado no primeiro valor)
                        if index !=0:
                            valor1 = operacao[:index]
                            op = operacao[index:index+2]
                            # O segundo valor também está grudado (ex:idade>=4)
                            relacao_.append(valor1)
                            relacao_.append(op)
                            if len(operacao) != index+2:
                                valor2 = operacao[index+2:]
                                relacao_.append(valor2)
                        # Se o tamanho da operacao é maior que 2, e o primeiro valor não está grudado,
                        #então o segundo valor está grudado.
                        else:
                            op = operacao[index:index+2]
                            valor2 = operacao[index+2:]
                            relacao_.append(op)
                            relacao_.append(valor2)
                for operador in ['>','<','=']:
                    if(flag):
                        break
                    if operador in operacao:
                        flag = True
                        index = operacao.find(operador)
                        valor1 = '' 
                        op = ''
                        valor2 = '' 
                        # idade>= (operador grudado no primeiro valor)
                        if index !=0:
                            valor1 = operacao[:index]
                            op = operacao[index:index+1]
                            relacao_.append(valor1)
                            relacao_.append(op)
                            # O segundo valor também está grudado (ex:idade>=4)
                            if len(operacao) != index+1:
                                valor2 = operacao[index+1:]
                                relacao_.append(valor2)
                        # Se o tamanho da operacao é maior que 2, e o primeiro valor não está grudado,
                        #então o segundo valor está grudado.
                        else:
                            op = operacao[index:index+1]
                            valor2 = operacao[index+1:]
                            relacao_.append(op)
                            relacao_.append(valor2)
                if not flag:
                    relacao_.append(operacao)
            else:
                relacao_.append(operacao)

        if len(relacao_)!= 0:
            interpretacaoFrom['join']['enable'] = True
        else:
            interpretacaoFrom['join']['enable'] = False

        for campo in relacao_:
            index = campo.find('.')
            if index != -1:
                interpretacaoFrom['join']['tabela'].append(campo[:index])
                interpretacaoFrom['join']['att'].append(campo[index+1:])
                continue
            if campo == '>=' or campo == '<=' or campo == '>' or campo == '<' or campo == '=' or campo == '!=':
                interpretacaoFrom['join']['op'].append(campo)
                continue
            interpretacaoFrom['join']['tabela'].append("")
            interpretacaoFrom['join']['att'].append(campo)
            
            
        return interpretacaoFrom

    def sanitizaComando(self,comando):
        while ',' in comando:
            index = comando.find(',')
            comando = comando[:index] + ';' + comando[index+1:]
            if comando[index-1] == ' ':
                comando = comando[:index-1:] + comando[index:]
                index -=1
            if comando[index+1] == ' ':
                comando = comando[:index+1] + comando[index+2:]

        comandoSeparados = comando.split(' ')
        comandosMaisSeparados = []
        
        for comando in comandoSeparados:
            if ';' in comando:
                for c in comando.split(';'):
                    comandosMaisSeparados.append(c)
                    comandosMaisSeparados.append(',')
                comandosMaisSeparados.pop()
            else:
                comandosMaisSeparados.append(comando)
                    
                    
        return comandosMaisSeparados

    def classificaComandos(self,comandosSeparados):
        _select = comandosSeparados[1:comandosSeparados.index('from')]
        _from = []
        _where = []
        _order = []

        #from vai do from até o where
        if 'where' in comandosSeparados:
            _from = comandosSeparados[comandosSeparados.index('from')+1:comandosSeparados.index('where')]
            if 'order' in comandosSeparados:
                _where = comandosSeparados[comandosSeparados.index('where')+1:comandosSeparados.index('order')]
                _order = comandosSeparados[comandosSeparados.index('order')+2:]     
            else:
                _where = comandosSeparados[comandosSeparados.index('where')+1:]
        elif 'order' in comandosSeparados:
            #from vai do from até o order
            _from = comandosSeparados[comandosSeparados.index('from')+1:comandosSeparados.index('order')]
            _order = comandosSeparados[comandosSeparados.index('order')+2:]
        else:
            #from vai do from até o final
            _from = comandosSeparados[comandosSeparados.index('from')+1:]
        '''
        where n.idade >= 3

        >	Maior que
        >=	Maior ou igual
        <	Menor que
        <=	Menor ou igual
        <> ou !=	Diferente de
        =	Igual
        LIKE	Busca um padrão parecido

        IN	Incluindo (múltiplos valores)
        NOT IN	Excluindo (múltiplos valores)
        BETWEEN	Entre dois valores
        IS NULL	Traz todos os valores nulos
        IS NOT NULL	Traz todos os valores que não são nulos
        ''' 

        #Sanitizar o where
        if(len(_where)!=0):
            if 'and' in _where:
                indice = _where.index('and')
                where1 = _where[:indice]
                where2 = _where[indice+1:]
                _where = []
                _where.append(where1)
                _where.append('and')
                _where.append(where2)
            elif 'or' in _where:
                indice = _where.index('or')
                where1 = _where[:indice]
                where2 = _where[indice+1:]
                _where = []
                _where.append(where1)
                _where.append('or')
                _where.append(where2)
            else:
                _where = [_where]
                   
        return _select,_from,_where,_order

#Com Tudo
#comando = "select s.name as nome,s.id as identificador, t.semester as semestre from student as s, takes as t where s.id = t.id and t.semester >= 'Spring' order by tabela.nome ASC"
#Sem Where
#comando = "select s.name as nome,s.id as identificador, t.semester as semestre from student as s, takes as t order by tabela.nome ASC"
#Sem Order by
#comando = "select s.name as nome,s.id as identificador, t.semester as semestre from student as s, takes as t where s.id > 4 and idade like '%oi'"
#Sem Nada
#comando = "select name ,semester as semestre from student , takes as t"

#i = Interpretador()
#i.interpretar(comando)

