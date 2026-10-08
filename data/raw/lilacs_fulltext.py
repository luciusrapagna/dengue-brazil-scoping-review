"""Full-text extraction of serotype information for the LILACS additions whose
abstract did not report it (8 October 2026). Full texts were read from SciELO,
the journal websites (OJS/PDF) or BVS repositories.

FULLTEXT_FOUND: bvs_index -> (serotype text, serotype-year evidence)
  '†' = extracted from the full text; '*' = attributed by analogy in the full text.
ACCESSED_NOT_REPORTED: full text read, serotype of the studied epidemic not reported.
NOT_ACCESSED: full text not available or not retrievable (paywall, server error, no link).
"""
T = " †"
FULLTEXT_FOUND = {
    5: ("DENV-1 (até 1997), DENV-1 e DENV-2 (1997–2001), DENV-3 (2002)" + T, [(1, 1996, 2001), (2, 1997, 2001), (3, 2002, 2002)]),
    17: ("DENV-3 (2006) e DENV-1 (2011)" + T, [(3, 2006, 2006), (1, 2011, 2011)]),
    41: ("DENV-3 predominante (2006–2007)" + T, [(3, 2006, 2007)]),
    49: ("DENV-2 predominante nos óbitos; DENV-1 e DENV-3" + T, [(1, 2006, 2006), (2, 2007, 2008), (3, 2007, 2007), (1, 2008, 2008)]),
    52: ("DENV-1, DENV-2 e DENV-3" + T, []),
    61: ("Três sorotipos cocirculantes (não especificados)" + T, []),
    69: ("DENV-1" + T, [(1, 2013, 2013)]),
    74: ("DENV-1 predominante" + T, [(1, 2018, 2022)]),
    78: ("DENV-1" + T, []),
    81: ("DENV-1 predominante" + T, [(1, 2017, 2022)]),
    82: ("DENV-1 e DENV-2" + T, []),
    91: ("DENV-1" + T, [(1, 1990, 1991)]),
    130: ("Vários (sorotipo analisado como variável)" + T, []),
    132: ("DENV-3" + T, [(3, 2006, 2006)]),
    145: ("DENV-2" + T, [(2, 2008, 2008)]),
    149: ("DENV-1 (2013)" + T, [(1, 2013, 2013)]),
    151: ("DENV-1 predominante; quatro sorotipos em 2013–2014" + T, [(1, 2007, 2015), (2, 2013, 2014), (3, 2013, 2014), (4, 2013, 2014)]),
    165: ("DENV-2 predominante e DENV-1" + T, [(2, 1994, 1994), (1, 1994, 1994)]),
    171: ("Vários (substituição de sorotipos precedendo os maiores surtos)" + T, []),
    172: ("DENV-2 (2008)*", []),
    174: ("DENV-1 e DENV-2 (2015)" + T, [(1, 2015, 2015), (2, 2015, 2015)]),
    178: ("DENV-1 (95%), DENV-3 e DENV-4" + T, []),
    180: ("DENV-1" + T, [(1, 1990, 1991)]),
    197: ("DENV-1 a DENV-4 em cocirculação" + T, []),
    203: ("DENV-2 (1995), DENV-1 (1996), DENV-3 (2003) e reintrodução do DENV-2 (2008)" + T, [(3, 2003, 2003), (2, 2008, 2009)]),
    206: ("DENV-3 (2006); DENV-1, DENV-2 e DENV-3 (2007)" + T, [(3, 2006, 2007), (1, 2007, 2007), (2, 2007, 2007)]),
    217: ("DENV-1, DENV-2 e DENV-3" + T, [(1, 2001, 2009), (2, 2001, 2009), (3, 2001, 2009)]),
    223: ("DENV-1, DENV-2 e DENV-3 (DENV-3 predominante na região metropolitana)" + T, []),
    237: ("DENV-2 (80%), DENV-1 e DENV-3" + T, []),
    243: ("Não identificado (declarado pelos autores)" + T, []),
    246: ("DENV-1 (92%), DENV-2 e DENV-3" + T, [(1, 2010, 2011), (2, 2010, 2011), (3, 2010, 2011)]),
    267: ("DENV-1 (60,4%), DENV-4 (22,1%), DENV-2 e DENV-3" + T, [(1, 2009, 2014), (4, 2011, 2014), (2, 2009, 2014), (3, 2009, 2014)]),
    277: ("DENV-1 (2015–2016); DENV-2 (2018–2019)" + T, [(1, 2015, 2016), (2, 2018, 2019)]),
    301: ("DENV-4" + T, [(4, 2011, 2011)]),
    311: ("DENV-1, DENV-2 e DENV-3" + T, []),
    313: ("Tipado em 1,2% dos casos" + T, []),
    315: ("DENV-3 (2002)" + T, [(3, 2002, 2002)]),
    321: ("DENV-3" + T, [(3, 2001, 2002)]),
    355: ("DENV-1 (1990) e DENV-2 (1997)" + T, [(1, 1990, 2002), (2, 1997, 2002)]),
    414: ("DENV-1, DENV-2 e DENV-3" + T, [(1, 2002, 2002), (2, 2002, 2002), (3, 2002, 2002)]),
    425: ("DENV-1 (1998) e DENV-2" + T, [(1, 1998, 1998), (2, 1998, 1998)]),
    449: ("DENV-1" + T, [(1, 1990, 1991)]),
}
NOT_ACCESSED = [2, 15, 86, 88, 104, 115, 140, 141, 163, 182, 264, 272, 284, 299, 300, 303, 305, 307,
                323, 329, 330, 373, 407, 419, 431, 433, 448, 452]
# every other addition without serotype in the abstract had its full text read without finding it
