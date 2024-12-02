% Hechos: Informaci�n sobre alimentos
% alimento(Nombre, Calor�as por 100g, Prote�nas (g), Grasas (g), Carbohidratos (g))
alimento('Manzana', 52, 0.3, 0.2, 14).
alimento('Pechuga de pollo', 165, 31, 3.6, 0).
alimento('Arroz integral', 123, 2.9, 1, 26).
alimento('Espinacas', 23, 2.9, 0.4, 3.6).
alimento('Yogur natural', 59, 10, 0.4, 3.6).
alimento('Avena', 389, 16.9, 6.9, 66.3).
alimento('Pl�tano', 89, 1.1, 0.3, 22.8).
alimento('Salm�n', 206, 22, 13, 0).
alimento('Almendras', 576, 21, 49, 22).
alimento('Br�coli', 34, 2.8, 0.4, 6.6).
alimento('Huevos', 155, 13, 11, 1.1).
alimento('Leche descremada', 42, 3.4, 0.1, 5).
alimento('Pan integral', 247, 13, 4.2, 41).
alimento('Quinoa', 120, 4.1, 1.9, 21.3).
alimento('Aceite de oliva', 884, 0, 100, 0).

% Hechos: Dietas predefinidas
% dieta(Nombre de la dieta, Lista de alimentos)
dieta('Dieta para Diabetes', ['Manzana', 'Pechuga de pollo', 'Espinacas', 'Yogur natural', 'Br�coli']).
dieta('Dieta para Hipertensi�n', ['Arroz integral', 'Espinacas', 'Pechuga de pollo', 'Pl�tano', 'Br�coli']).
dieta('Dieta para Colesterol alto', ['Espinacas', 'Manzana', 'Yogur natural', 'Salm�n', 'Avena']).
dieta('Dieta Balanceada', ['Arroz integral', 'Pechuga de pollo', 'Manzana', 'Huevos', 'Quinoa']).
dieta('Dieta para P�rdida de Peso', ['Espinacas', 'Br�coli', 'Huevos', 'Manzana', 'Leche descremada']).
dieta('Dieta para Aumento de Masa Muscular', ['Pechuga de pollo', 'Huevos', 'Quinoa', 'Leche descremada', 'Salm�n']).
dieta('Dieta Vegana', ['Avena', 'Almendras', 'Espinacas', 'Quinoa', 'Br�coli']).

% Hechos: Condiciones de salud y sus dietas recomendadas
condicion_dieta('Diabetes', 'Dieta para Diabetes').
condicion_dieta('Hipertensi�n', 'Dieta para Hipertensi�n').
condicion_dieta('Colesterol alto', 'Dieta para Colesterol alto').
condicion_dieta('Sobrepeso', 'Dieta para P�rdida de Peso').
condicion_dieta('Obesidad', 'Dieta para P�rdida de Peso').
condicion_dieta('Aumento muscular', 'Dieta para Aumento de Masa Muscular').
condicion_dieta('Vegano', 'Dieta Vegana').
condicion_dieta('Normal', 'Dieta Balanceada').

% Regla: Recomendar una dieta completa en funci�n de la condici�n de salud y calor�as objetivo
recomendar_dieta(Condicion, CaloriasObjetivo, Dieta, DietaAjustada) :-
    condicion_dieta(Condicion, Dieta),
    dieta(Dieta, Alimentos),
    ajustar_dieta(Alimentos, CaloriasObjetivo, DietaAjustada).

% Regla: Ajustar dietas seg�n calor�as objetivo
ajustar_dieta(Alimentos, CaloriasObjetivo, DietaAjustada) :-
    incluir_calorias(Alimentos, 0, CaloriasTotales),
    CaloriasTotales =< CaloriasObjetivo,
    DietaAjustada = Alimentos.

% Calcular calor�as totales de una lista de alimentos
incluir_calorias([], Calorias, Calorias).
incluir_calorias([Alimento|Resto], CaloriasAcumuladas, CaloriasTotales) :-
    alimento(Alimento, CaloriasAlimento, _, _, _),
    CaloriasNuevas is CaloriasAcumuladas + CaloriasAlimento,
    incluir_calorias(Resto, CaloriasNuevas, CaloriasTotales).

% Regla: Sugerir alimentos adicionales si las calor�as de la dieta ajustada son muy bajas
sugerir_alimentos(AlimentosBase, CaloriasObjetivo, AlimentosFinales) :-
    incluir_calorias(AlimentosBase, 0, CaloriasTotales),
    CaloriasTotales < CaloriasObjetivo,
    findall(Alimento, alimento(Alimento, _, _, _, _), TodosLosAlimentos),
    seleccionar_alimentos(TodosLosAlimentos, AlimentosBase, CaloriasObjetivo, AlimentosFinales).

seleccionar_alimentos([], Alimentos, _, Alimentos).
seleccionar_alimentos([Alimento|Resto], AlimentosActuales, CaloriasObjetivo, AlimentosFinales) :-
    \+ member(Alimento, AlimentosActuales),
    alimento(Alimento, CaloriasAlimento, _, _, _),
    incluir_calorias(AlimentosActuales, CaloriasAcumuladas, _),
    CaloriasAcumuladas + CaloriasAlimento =< CaloriasObjetivo,
    seleccionar_alimentos(Resto, [Alimento|AlimentosActuales], CaloriasObjetivo, AlimentosFinales).
seleccionar_alimentos([_|Resto], AlimentosActuales, CaloriasObjetivo, AlimentosFinales) :-
    seleccionar_alimentos(Resto, AlimentosActuales, CaloriasObjetivo, AlimentosFinales).
