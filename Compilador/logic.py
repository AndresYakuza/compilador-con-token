import re
import sympy

# Definiciones de tipos de tokens
TOKEN_TYPES = [
    ('VARIABLE', r'[a-z]\w*'),
    ('ENTERO', r'\d+'),
    ('REAL', r'\d+\.\d+'),
    ('TEXTO', r'"[^"]*"'),
    ('TIPO', r'\b(Entero|Texto|Real)\b'),
    ('OPERADOR', r'[+\-*/]'),
    ('IGUAL', r'='),
    ('PUNTO_COMA', r';'),
    ('PARENTESIS_ABIERTO', r'\('),
    ('PARENTESIS_CERRADO', r'\)'),
    ('CAPTURA', r'\bCaptura\.(Entero|Texto|Real)\(\)'),
    ('MENSAJE_TEXTO', r'\bMensaje\.Texto\b'),
    ('ESPACIO', r'\s+'),  # Espacios y tabulaciones
]

# Expresión regular combinada para todos los tokens
TOKEN_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_TYPES)

def tokenize(line):
    tokens = []
    for match in re.finditer(TOKEN_REGEX, line):
        token_type = match.lastgroup
        token_value = match.group(token_type)
        if token_type != 'ESPACIO':  # Ignorar espacios
            tokens.append((token_type, token_value))
    return tokens

class CodeEditorLogic:
    def __init__(self, gui):
        self.gui = gui  # Almacena la referencia de la GUI

    def validate_code(self):
        code = self.gui.code_editor.get("1.0", "end-1c")
        lines = code.split("\n")
        errors = []
        declared_variables = {}
        used_variables = set()

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Tokenizar la línea de código
            tokens = tokenize(line)
            print(f"Line {i + 1} tokens: {tokens}") 

            if not tokens:
                continue

            token_types = [t[0] for t in tokens]
            token_values = [t[1] for t in tokens]

            # Procesar tokens para validar declaraciones de variables
            if token_types == ['VARIABLE', 'TIPO', 'PUNTO_COMA']:
                variable_name, variable_type = token_values[0], token_values[1]
                if variable_name in declared_variables:
                    errors.append(f"Error en línea {i + 1}: Variable '{variable_name}' ya declarada")
                elif not variable_name[0].islower():
                    errors.append(f"Error en línea {i + 1}: El nombre de la variable debe comenzar con una letra minúscula")
                declared_variables[variable_name] = variable_type

            # Procesar tokens para asignaciones de valores
            elif token_types == ['VARIABLE', 'IGUAL', 'ENTERO', 'PUNTO_COMA'] or \
                 token_types == ['VARIABLE', 'IGUAL', 'REAL', 'PUNTO_COMA'] or \
                 token_types == ['VARIABLE', 'IGUAL', 'TEXTO', 'PUNTO_COMA']:
                variable_name, value = token_values[0], token_values[2]
                if variable_name not in declared_variables:
                    errors.append(f"Error en línea {i + 1}: Variable '{variable_name}' no declarada")
                elif (declared_variables[variable_name] == "Entero" and not value.isnumeric()) or \
                     (declared_variables[variable_name] == "Texto" and not (value.startswith('"') and value.endswith('"'))) or \
                     (declared_variables[variable_name] == "Real" and not (re.match(r'^\d+(\.\d+)?$', value))):
                    errors.append(f"Error en línea {i + 1}: Asignación incorrecta a '{variable_name}'")
                used_variables.add(variable_name)

            # Procesar tokens para asignaciones de variables a otras variables del mismo tipo
            elif token_types == ['VARIABLE', 'IGUAL', 'VARIABLE', 'PUNTO_COMA']:
                var_destino, var_origen = token_values[0], token_values[2]
                if var_destino not in declared_variables:
                    errors.append(f"Error en línea {i + 1}: Variable '{var_destino}' no declarada")
                elif var_origen not in declared_variables:
                    errors.append(f"Error en línea {i + 1}: Variable '{var_origen}' no declarada")
                elif declared_variables[var_destino] != declared_variables[var_origen]:
                    errors.append(f"Error en línea {i + 1}: Asignación tipos de variable diferentes")
                used_variables.add(var_destino)
                used_variables.add(var_origen)

            # Procesar tokens para asignaciones utilizando Captura
            elif token_types == ['VARIABLE', 'IGUAL', 'CAPTURA', 'PUNTO_COMA']:
                nombre_variable, tipo_captura = token_values[0], tokens[2][1].split('.')[1].rstrip('()')
                if nombre_variable not in declared_variables:
                    errors.append(f"Error en línea {i + 1}: Variable '{nombre_variable}' no declarada")
                elif declared_variables[nombre_variable] != tipo_captura:
                    errors.append(f"Error en línea {i + 1}: Asignación tipos de variable diferentes")
                used_variables.add(nombre_variable)

            # Procesar tokens para operaciones matemáticas
            elif token_types[1] == 'IGUAL' and token_types[-1] == 'PUNTO_COMA':
                nombre_variable = token_values[0]
                operacion = ' '.join(token_values[2:-1])
                if nombre_variable not in declared_variables:
                    errors.append(f"Error en línea {i + 1}: Variable '{nombre_variable}' no declarada")
                if 'Captura' in operacion:
                    errors.append(f"Error en línea {i + 1}: No se puede usar Captura en operaciones matemáticas")
                else:
                    try:
                        sympy.sympify(operacion)
                        used_variables.add(nombre_variable)
                    except (ValueError, SyntaxError):
                        errors.append(f"Error en línea {i + 1}: Sintaxis incorrecta en la operación matemática")

            # Procesar tokens para la función Mensaje.Texto
            elif token_types == ['MENSAJE_TEXTO', 'PARENTESIS_ABIERTO', 'VARIABLE', 'PARENTESIS_CERRADO', 'PUNTO_COMA'] or \
                 token_types == ['MENSAJE_TEXTO', 'PARENTESIS_ABIERTO', 'TEXTO', 'PARENTESIS_CERRADO', 'PUNTO_COMA']:
                mensaje = token_values[2]
                if not (mensaje.startswith('"') and mensaje.endswith('"')) and mensaje not in declared_variables:
                    errors.append(f"Error en línea {i + 1}: Variable '{mensaje}' no declarada")
                used_variables.add(mensaje)

            else:
                errors.append(f"Error en línea {i + 1}: Sintaxis incorrecta")

        unused_variables = set(declared_variables.keys()) - used_variables
        if not errors:
            self.gui.console.config(state="normal")
            self.gui.console.delete("1.0", "end")
            self.gui.console.insert("end", "La Sintaxis es correcta\n")
            if unused_variables:
                self.gui.console.insert("end", f"Advertencia: Variables declaradas pero no utilizadas: {', '.join(unused_variables)}\n")
            self.gui.console.config(state="disabled")
        else:
            self.gui.console.config(state="normal")
            self.gui.console.delete("1.0", "end")
            for error in errors:
                self.gui.console.insert("end", error + "\n")
            self.gui.console.config(state="disabled")

    def compile_code(self):
        pass

