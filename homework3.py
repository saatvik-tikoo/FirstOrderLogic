class KnowledgeBase:
    def __init__(self):
        self.axioms = []

    def add_axiom(self, axiom, idx):
        if '=>' in axiom:
            temp = axiom[: axiom.index(' =')].split(' & ')
            new_axiom = ''
            for i in temp:
                if i[0] == '~':
                    new_axiom += i[1:] + '|'
                else:
                    new_axiom += '~' + i + '|'
            axiom = new_axiom + axiom[axiom.index('>') + 2:]
            predicates = axiom.split('|')
            new_pred = ''
            for i in predicates:
                args = i[i.index('(') + 1: i.index(')')].split(',')
                res = ''
                for j in range(len(args)):
                    if args[j][0].islower():
                        res += args[j] + str(idx) + ','
                    else:
                        res += args[j] + ','
                if res[-1] == ',':
                    res = res[: -1]
                new_pred += i[: i.index('(') + 1] + res + i[i.index(')'):] + '|'
            if new_pred[: -1] not in self.axioms:
                self.axioms.append(new_pred[: -1])
        else:
            if axiom not in self.axioms:
                self.axioms.append(axiom)

    def get_all_axioms(self):
        return self.axioms

    def get_size(self):
        return len(self.axioms)

def get_input():
    with open('input.txt', 'r') as fread:
        t_queries = int(fread.readline().strip())
        q = []
        for idx in range(t_queries):
            q.append(fread.readline().strip())
        t_kb = int(fread.readline().strip())
        kb_obj = KnowledgeBase()
        for idx in range(t_kb):
            kb_obj.add_axiom(fread.readline().strip(), idx)
    return t_queries, q, t_kb, kb_obj, idx

def negate_the_query(query):
    if query[0] == '~':
        return query[1:]
    else:
        return '~' + query

def print_output(res):
    with open('output.txt', 'w') as fwrite:
        for idx in range(len(res)):
            fwrite.write(res[idx])
            if idx < len(res) - 1:
                fwrite.write('\n')

def variable_unification(variable, sub, substitution):
    if variable in substitution:
        return unifiable(substitution[variable], sub, substitution)
    elif x in substitution:
        return unifiable(variable, substitution[sub], substitution)
    else:
        substitution[variable] = sub
        return substitution

def unifiable(pred_query_args, pred_sentence_args, substitution):
    if substitution == False:
        return False
    elif pred_query_args == pred_sentence_args:
        return substitution
    elif isinstance(pred_query_args, str) and pred_query_args.islower():
        return variable_unification(pred_query_args, pred_sentence_args, substitution)
    elif isinstance(pred_sentence_args, str) and pred_sentence_args.islower():
        return variable_unification(pred_sentence_args, pred_query_args, substitution)
    elif isinstance(pred_query_args, list) and isinstance(pred_sentence_args, list):
        if pred_query_args and pred_sentence_args:
            return unifiable(pred_query_args[1:], pred_sentence_args[1:], unifiable(pred_query_args[0], pred_sentence_args[0], substitution))
        else:
            return substitution
    else:
        return False

def substitute_and_resolve(sentence, query, substitution, pred_query, pred_sentence):
    predicates_of_sentence = sentence.split('|')
    sent_temp = []
    cnt = 0
    for ix in predicates_of_sentence:
        if cnt == 0 and ix == pred_sentence:
            cnt += 1
        else:
            sent_temp.append(ix)
    new_sentence = '|'.join(sent_temp)

    predicates_of_query = query.split('|')
    q_temp = []
    cnt = 0
    for ix in predicates_of_query:
        if cnt == 0 and ix == pred_query:
            cnt += 1
        else:
            q_temp.append(ix)
    new_query = '|'.join(q_temp)
    if new_query == '' and new_sentence == '':
        return ''
    elif new_query != '' and new_sentence == '':
        new_sentence = new_query
    elif new_query != '' and new_sentence != '':
        new_sentence += '|' + new_query
    new_sentence_predicates = new_sentence.split('|')
    res = set()
    for cur_pred in new_sentence_predicates:
        arguments = cur_pred.split('(')[1][: -1].split(',')
        new_arguments = []
        for var in arguments:
            if var in substitution:
                new_arguments.append(substitution[var])
            else:
                new_arguments.append(var)
        resultant_args = ','.join(new_arguments)
        res.add(cur_pred.split('(')[0] + '(' + resultant_args + ')')
    return '|'.join(res)

visited = set()

def resolution(query, kb):
    if query in visited:
        return False
    if query == '':
        return True
    if query in kb:
        return False
    if len(query.split('|')) == 1 and negate_the_query(query) in kb:
        return True
    if query not in kb:
        kb.append(query)
    predicates_query = set(query.split('|'))
    kb = change_kb(kb)
    for pred_query in predicates_query:
        pred_query_name = pred_query.split('(')[0]
        pred_query_args = pred_query.split('(')[1][: -1].split(',')
        for sentence in kb:
            predicates_sentence = set(sentence.split('|'))
            for pred_sentence in predicates_sentence:
                pred_sentence_name = pred_sentence.split('(')[0]
                pred_sentence_args = pred_sentence.split('(')[1][: -1].split(',')
                if (pred_query_name == '~' + pred_sentence_name or pred_sentence_name == '~' + pred_query_name) \
                        and len(pred_query_args) == len(pred_sentence_args):
                    substitution = dict()
                    substitution = unifiable(pred_query_args, pred_sentence_args, substitution)
                    if substitution != False:
                        answer = substitute_and_resolve(sentence, query, substitution, pred_query, pred_sentence)
                        if resolution(answer, kb):
                            return True
        visited.add(query)
        return False

def change_kb(kb):
    const_sent = []
    for ix in kb:
        cnt = 0
        total_len = 0
        predicates = ix.split('|')
        for p in predicates:
            args = p.split('(')[1][: -1].split(',')
            total_len += len(args)
            for a in args:
                if a.isupper():
                    cnt += 1
        if cnt == total_len:
            const_sent.append(ix)
    for ix in kb:
        if ix not in const_sent:
            const_sent.append(ix)
    return const_sent


if __name__ == '__main__':
    total_queries, queries, kb_size, knowledge_base, var_num = get_input()
    result = []
    for x in range(total_queries):
        # Negate the give query
        if queries[x] is None or queries[x] == '':
            result.append('TRUE')
        else:
            contradiction = negate_the_query(queries[x])
            temporary_kb = list(knowledge_base.get_all_axioms())
            visited = set()
            ans = resolution(contradiction, temporary_kb)
            if ans:
                result.append('TRUE')
            else:
                result.append('FALSE')
            if ans:
                var_num += 1
                knowledge_base.add_axiom(queries[x], var_num)

    print_output(result)
