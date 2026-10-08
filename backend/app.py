from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///petshop.db"

db = SQLAlchemy(app)


class Dono(db.Model):
    __tablename__ = "donos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)

    pets = db.relationship("Pet", backref="dono")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone
        }


class Pet(db.Model):
    __tablename__ = "pets"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    dono_id = db.Column(db.Integer, db.ForeignKey("donos.id"),
                        nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "especie": self.especie,
            "idade": self.idade,
            "dono_id": self.dono_id,
            "dono_nome": self.dono.nome
        }


@app.route("/donos", methods=["GET"])
def listar_donos():
    todos_os_donos = Dono.query.all()
    return jsonify([dono.to_dict() for dono in todos_os_donos])


@app.route("/donos/<int:dono_id>", methods=["GET"])
def buscar_dono(dono_id):
    dono_encontrado = db.session.get(Dono, dono_id)

    if dono_encontrado is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    return jsonify(dono_encontrado.to_dict())


@app.route("/donos", methods=["POST"])
def cadastrar_dono():
    corpo = request.json

    if not corpo or "nome" not in corpo or "telefone" not in corpo:
        return jsonify({"erro": "Informe nome e telefone"}), 400

    dono_cadastrado = Dono(nome=corpo["nome"], telefone=corpo["telefone"])

    db.session.add(dono_cadastrado)
    db.session.commit()

    return jsonify(dono_cadastrado.to_dict()), 201


@app.route("/donos/<int:dono_id>", methods=["PUT"])
def atualizar_dono(dono_id):
    corpo = request.json

    if not corpo or "nome" not in corpo or "telefone" not in corpo:
        return jsonify({"erro": "Informe nome e telefone"}), 400

    dono_encontrado = db.session.get(Dono, dono_id)

    if dono_encontrado is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    dono_encontrado.nome = corpo["nome"]
    dono_encontrado.telefone = corpo["telefone"]
    db.session.commit()

    return jsonify(dono_encontrado.to_dict())


@app.route("/donos/<int:dono_id>", methods=["DELETE"])
def remover_dono(dono_id):
    dono_encontrado = db.session.get(Dono, dono_id)

    if dono_encontrado is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    db.session.delete(dono_encontrado)
    db.session.commit()

    return jsonify({"mensagem": "Dono removido com sucesso"})


CAMPOS_OBRIGATORIOS_PET = ("nome", "especie", "idade", "dono_id")


def corpo_do_pet_esta_completo(corpo):
    return bool(corpo) and all(campo in corpo for campo in CAMPOS_OBRIGATORIOS_PET)


@app.route("/pets", methods=["GET"])
def listar_pets():
    filtro_dono = request.args.get("dono_id")

    if filtro_dono is None:
        pets_listados = Pet.query.all()
    else:
        try:
            filtro_dono = int(filtro_dono)
        except ValueError:
            return jsonify({"erro": "dono_id deve ser um numero"}), 400

        pets_listados = Pet.query.filter_by(dono_id=filtro_dono).all()

    return jsonify([pet.to_dict() for pet in pets_listados])


@app.route("/pets/<int:pet_id>", methods=["GET"])
def buscar_pet(pet_id):
    pet_encontrado = db.session.get(Pet, pet_id)

    if pet_encontrado is None:
        return jsonify({"erro": "Pet nao encontrado"}), 404

    return jsonify(pet_encontrado.to_dict())


@app.route("/pets", methods=["POST"])
def cadastrar_pet():
    corpo = request.json

    if not corpo_do_pet_esta_completo(corpo):
        return jsonify(
            {"erro": "Informe nome, especie, idade e dono_id"}), 400

    if db.session.get(Dono, corpo["dono_id"]) is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    pet_cadastrado = Pet(
        nome=corpo["nome"],
        especie=corpo["especie"],
        idade=corpo["idade"],
        dono_id=corpo["dono_id"]
    )

    db.session.add(pet_cadastrado)
    db.session.commit()

    return jsonify(pet_cadastrado.to_dict()), 201


@app.route("/pets/<int:pet_id>", methods=["PUT"])
def atualizar_pet(pet_id):
    corpo = request.json

    if not corpo_do_pet_esta_completo(corpo):
        return jsonify(
            {"erro": "Informe nome, especie, idade e dono_id"}), 400

    pet_encontrado = db.session.get(Pet, pet_id)

    if pet_encontrado is None:
        return jsonify({"erro": "Pet nao encontrado"}), 404

    if db.session.get(Dono, corpo["dono_id"]) is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    pet_encontrado.nome = corpo["nome"]
    pet_encontrado.especie = corpo["especie"]
    pet_encontrado.idade = corpo["idade"]
    pet_encontrado.dono_id = corpo["dono_id"]
    db.session.commit()

    return jsonify(pet_encontrado.to_dict())


@app.route("/pets/<int:pet_id>", methods=["DELETE"])
def remover_pet(pet_id):
    pet_encontrado = db.session.get(Pet, pet_id)

    if pet_encontrado is None:
        return jsonify({"erro": "Pet nao encontrado"}), 404

    db.session.delete(pet_encontrado)
    db.session.commit()

    return jsonify({"mensagem": "Pet removido com sucesso"})


if __name__ == "__main__":
    app.run(debug=True)
