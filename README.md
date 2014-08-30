quesedijo
=========

Nubes de palabras temporales y comparativas


Entradas
--------

 * Fuentes
   * Nombre
   * Listas de documentos
     * Documento
       * Fecha
       * Campos
         key, valor
 * Ponderaciones: lista de (campo, peso)
 * Tokenizer
 * Agrupación temporal (día, semana, mes, año)


def calculate_source_cloud(documents):
    source_tag_cloud = {}

    for timegroup, documents in groupby(source.get_document(), key=group_fn):
        tag_cloud = {}
        for doc in documents:
            for field, value in documents.get_fields():
                tokens = tokenizer(value)
                for token, count in tokens:
                    tag_cloud[token] = tag_cloud.get(token, 0) + field_weights[field] * count
        source_tag_cloud[timegroup] = tag_cloud
    return source_tag_cloud



URLs de ejemplo
---------------

De RSS:

 * http://radiocut.fm/feeds/q?radio=nacional870&start=365&limit=10000
 * http://radiocut.fm/feeds/q?radio=mitre&start=365&limit=10000

