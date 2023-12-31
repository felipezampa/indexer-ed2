from math import log
from utils import sanitize_line
from classes import Trie, FrequencyTable, Word
import operator

def freq(trie: Trie, frequency):
    '''
      Calcula a frequência das palavras nos arquivos e exibe as palavras mais frequentes.
    '''
    freq_table = FrequencyTable(frequency)

    for file_obj in trie.files:
        with open(file_obj.name, "r", encoding="utf-8") as file:

            for line in file:
                # Remove caracteres especiais e palavras com menos de 3 caracteres da linha
                line = sanitize_line(line)

                for word in line:
                    if len(word) > 2:
                        word_obj = trie.insert_word(word, file_obj)
                        freq_table.insert_word(word_obj)
    # Exibe as palavras mais frequentes na tabela de frequência
    freq_table.print()

def freq_word(trie: Trie, word_frequency):
    '''
      Exibe o número de ocorrências de uma palavra específica nos arquivos.
    '''
    for file_obj in trie.files:
        with open(file_obj.name, "r", encoding="utf-8") as file:
            for line in file:
                line = sanitize_line(line)
                for word in line:
                    if len(word) > 2:
                        trie.insert_word(word, file_obj)
    
    word = trie.word_exists(word_frequency)
    if word:
        print("Aparicoes da palavra {}: {}".format(word.word, word.overall_frequency))
    else:
        print("Palavra nao encontrada")

def calc_tf(trie: Trie, word_obj: Word, file_index: str):
    '''
      Calcula o Term Frequency (TF) de uma palavra em um arquivo específico.
      Term Frequency (TF) ou Frequência de um termo t, ] deve ser calculada como o 
      número de vezes que t aparece no documento, dividido pelo número total de palavras no documento:
    '''
    file = trie.files[int(file_index)]
    word_occurrences_in_file = word_obj.files[file_index]
    return  word_occurrences_in_file / file.word_count

def calc_idf(trie: Trie, word_obj: Word):
    '''
      Calcula o Inverse Document Frequency (IDF) de uma palavra.
      Inverse Document Frequency (IDF) ou Frequência inversa de documento para um conjunto de documentos 
      D é o logaritmo da divisão do número total de documentos pelo número de documentos que contém o termo t em questão:
    '''
    file_count = trie.file_count
    n_files_word_present = word_obj.file_count
    return log(file_count/n_files_word_present, 10)

def search(trie: Trie, search_word: Word):
    '''
     Realiza uma pesquisa ponderada usando TF-IDF e exibe os resultados.
    '''
    for file_obj in trie.files:
        with open(file_obj.name, "r", encoding="utf-8") as file:
            for line in file:
                line = sanitize_line(line)

                for word in line:
                    if len(word) > 2:
                       trie.insert_word(word, file_obj)

    words = sanitize_line(search_word)

    files_tfidf = {}
    for word in words:
        word_obj = trie.word_exists(word)
        if not word_obj:
            print("Palavra não encontrada no arquivo.")
            return 0
        word_obj.idf = calc_idf(trie, word_obj)
        for i in range(trie.file_count):
            dict_key_index = str(i)
            if dict_key_index in word_obj.files.keys():
                tf = calc_tf(trie, word_obj, dict_key_index)
                if dict_key_index in files_tfidf.keys():
                    files_tfidf[dict_key_index] = (tf * word_obj.idf + files_tfidf[dict_key_index]) / 2
                else:
                    files_tfidf[dict_key_index] = tf * word_obj.idf
    files_tfidf = dict(sorted(files_tfidf.items(), key=operator.itemgetter(1), reverse=True))

    for file in trie.files:
        if file.hashed_name in files_tfidf.keys():
            print("{} - {}".format(file.name, files_tfidf[file.hashed_name]))

