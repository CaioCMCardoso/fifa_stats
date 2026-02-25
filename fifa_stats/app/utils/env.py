import os
import ast
import warnings
from typing import TypeVar, Type

T = TypeVar("T")


def get(type_: Type[T], var_name: str, default: any = None) -> T:
    """
    Obtém um valor de tipo T a partir de uma variável de ambiente.

    Essa função encapsula o processo de validar e obter um valor concreto a partir dos
    argumentos fornecidos. A string passada como argumento deve conter um valor válido
    para o tipo T desejado.

    Args:
        ``type_`` (T) : Tipo do valor desejado após ser convertido
        ``var_name`` (str) : O nome da variável de ambiente a ser extraída
        ``default`` (T): Valor a ser usado caso a variável de ambiente não seja encontrada.

    Retorno:
        O valor literal da string contida na variável de ambiente. Caso a variável não
        seja encontrada, será usado o default se este não possuir valor None.

    Raises:
        ``TypeError:`` Caso o valor contido na variável não seja um 'T' válido.
        ``ValueError:`` Caso o valor contido na variável seja uma expressão inválida e
        o tipo pretendido não seja bool.
        ``KeyError:`` Caso a variável de ambiente não seja encontrada e um default não
        foi definido.
        ``RuntimeWarning:`` Caso a variável de ambiente não seja encontrada e o default
        precisou ser usado.

    """
    # Limita a conversão aos tipos primitivos
    if type_ not in [str, int, float, complex, bool, tuple, dict, list, set]:
        raise TypeError(f"O tipo {type_.__name__} não é suportado.")

    try:
        value_as_str: str = os.environ[var_name]

        return _parse(value_as_str, type_)
    except KeyError:  # pragma: no cover
        if default is not None:
            message = f"A variável de ambiente '{var_name}' não foi encontrada. O valor '{default}' "
            message = message + f"será usado e pode não ser válido para o tipo '{type_.__name__}'"
            warnings.warn(
                message,
                RuntimeWarning,
            )
            return default
        else:
            raise KeyError(f"A variável de ambiente '{var_name}' não foi encontrada.") from None
    except TypeError:  # pragma: no cover
        raise TypeError(
            f"A variável de ambiente '{var_name}' possui o valor '{value_as_str}', que é inválido para o tipo '{type_.__name__}'."
        ) from None
    except ValueError:  # pragma: no cover
        raise ValueError(
            (
                f"A variável de ambiente '{var_name}' possui o valor '{value_as_str}'",
                ", que é uma expressão inválida e não pode ser interpretada."
            )
        ) from None


def _parse(value_as_str: str, intended_type: T) -> T:
    """
    Obtém uma variável de tipo T a partir de uma string.

    Essa função encapsula o processo de validar e obter um valor concreto a partir dos
    argumentos fornecidos. A string passada como argumento deve conter um valor válido
    para o tipo T desejado.

    Args:
        ``value_as_str`` (str) : Valor a ser convertido, passado como uma string
        ``intended_type`` (T) : Tipo da variável a ser retornada pela função

    Retorno:
        O valor literal da string passada, de tipo T

    Raises:
        ``TypeError:`` Caso o valor contido na string não seja um 'T' válido.
        ``ValueError:`` Caso o valor contido na string cause erro ao ser processado
        pelo ast.literal_eval()
    """
    if intended_type is bool:
        bool_values = {"true": True, "false": False}

        if value_as_str.lower() in bool_values.keys():
            return bool_values[value_as_str.lower()]
        else:
            raise TypeError()

    elif intended_type is str:
        # Não aceita strings vazias
        if value_as_str:
            return value_as_str
        else:
            raise TypeError()

    else:
        try:
            concrete_value: any = ast.literal_eval(value_as_str)
        except Exception:  # pragma: no cover
            raise ValueError()

        if type(concrete_value) is intended_type:
            return concrete_value
        else:
            raise TypeError()
