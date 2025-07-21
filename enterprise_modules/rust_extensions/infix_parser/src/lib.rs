use pyo3::prelude::*;
use pyo3::types::PyDict;

/// Simple AST node
#[derive(Debug, Clone)]
enum Expr {
    Number(f64),
    Unary { op: char, expr: Box<Expr> },
    Binary { op: char, left: Box<Expr>, right: Box<Expr> },
}

fn tokenize(expr: &str) -> Vec<String> {
    let mut tokens = Vec::new();
    let mut current = String::new();
    for c in expr.chars() {
        if c.is_whitespace() {
            continue;
        } else if c.is_ascii_digit() || c == '.' {
            current.push(c);
        } else {
            if !current.is_empty() {
                tokens.push(current.clone());
                current.clear();
            }
            tokens.push(c.to_string());
        }
    }
    if !current.is_empty() {
        tokens.push(current);
    }
    tokens
}

fn parse_expression(tokens: &[String]) -> (Expr, usize) {
    parse_add_sub(tokens, 0)
}

fn parse_add_sub(tokens: &[String], mut pos: usize) -> (Expr, usize) {
    let (mut node, mut p) = parse_mul_div(tokens, pos);
    pos = p;
    while pos < tokens.len() {
        let op = tokens[pos].chars().next().unwrap();
        if op == '+' || op == '-' {
            let (rhs, np) = parse_mul_div(tokens, pos + 1);
            node = Expr::Binary { op, left: Box::new(node), right: Box::new(rhs) };
            pos = np;
        } else {
            break;
        }
    }
    (node, pos)
}

fn parse_mul_div(tokens: &[String], mut pos: usize) -> (Expr, usize) {
    let (mut node, mut p) = parse_unary(tokens, pos);
    pos = p;
    while pos < tokens.len() {
        let op = tokens[pos].chars().next().unwrap();
        if op == '*' || op == '/' {
            let (rhs, np) = parse_unary(tokens, pos + 1);
            node = Expr::Binary { op, left: Box::new(node), right: Box::new(rhs) };
            pos = np;
        } else {
            break;
        }
    }
    (node, pos)
}

fn parse_unary(tokens: &[String], mut pos: usize) -> (Expr, usize) {
    if pos < tokens.len() {
        let op = tokens[pos].chars().next().unwrap();
        if op == '+' || op == '-' {
            let (expr, p) = parse_unary(tokens, pos + 1);
            return (Expr::Unary { op, expr: Box::new(expr) }, p);
        }
    }
    parse_primary(tokens, pos)
}

fn parse_primary(tokens: &[String], pos: usize) -> (Expr, usize) {
    let token = &tokens[pos];
    if token == "(" {
        let (expr, mut p) = parse_expression(&tokens[pos + 1..]);
        p += pos + 1;
        if tokens[p] != ")" {
            panic!("expected )");
        }
        return (expr, p + 1);
    }
    let value: f64 = token.parse().unwrap();
    (Expr::Number(value), pos + 1)
}

fn simplify(expr: Expr) -> Expr {
    match expr {
        Expr::Binary { op, left, right } => {
            let left = simplify(*left);
            let right = simplify(*right);
            if let (Expr::Number(a), Expr::Number(b)) = (&left, &right) {
                let res = match op {
                    '+' => a + b,
                    '-' => a - b,
                    '*' => a * b,
                    '/' => a / b,
                    _ => unreachable!(),
                };
                Expr::Number(res)
            } else {
                Expr::Binary { op, left: Box::new(left), right: Box::new(right) }
            }
        }
        Expr::Unary { op, expr } => {
            let expr = simplify(*expr);
            if let Expr::Number(n) = &expr {
                let res = match op {
                    '+' => *n,
                    '-' => -*n,
                    _ => unreachable!(),
                };
                Expr::Number(res)
            } else {
                Expr::Unary { op, expr: Box::new(expr) }
            }
        }
        other => other,
    }
}

fn to_py<'p>(py: Python<'p>, expr: Expr) -> PyObject {
    match expr {
        Expr::Number(n) => {
            let dict = PyDict::new(py);
            dict.set_item("type", "Number").unwrap();
            dict.set_item("value", n).unwrap();
            dict.into()
        }
        Expr::Unary { op, expr } => {
            let dict = PyDict::new(py);
            dict.set_item("type", "Unary").unwrap();
            dict.set_item("op", op.to_string()).unwrap();
            dict.set_item("expr", to_py(py, *expr)).unwrap();
            dict.into()
        }
        Expr::Binary { op, left, right } => {
            let dict = PyDict::new(py);
            dict.set_item("type", "Binary").unwrap();
            dict.set_item("op", op.to_string()).unwrap();
            dict.set_item("left", to_py(py, *left)).unwrap();
            dict.set_item("right", to_py(py, *right)).unwrap();
            dict.into()
        }
    }
}

#[pyfunction]
fn parse_infix(expression: &str) -> PyObject {
    let tokens = tokenize(expression);
    let (expr, pos) = parse_expression(&tokens);
    if pos != tokens.len() {
        panic!("unexpected tokens at end");
    }
    let simplified = simplify(expr);
    Python::with_gil(|py| to_py(py, simplified))
}

#[pymodule]
fn infix_parser(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_infix, m)?)?;
    Ok(())
}
