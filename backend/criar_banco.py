from app import app, db, Dono, Pet

with app.app_context():
    db.create_all()

    if Dono.query.first() is None:
        dona_ana = Dono(nome="Ana Paula Ribeiro", telefone="45999110001")
        dono_bruno = Dono(nome="Bruno Martins", telefone="45999110002")

        db.session.add(dona_ana)
        db.session.add(dono_bruno)
        db.session.commit()

        pet_rex = Pet(nome="Rex", especie="cachorro", idade=4, dono_id=dona_ana.id)
        pet_mimi = Pet(nome="Mimi", especie="gato", idade=2, dono_id=dona_ana.id)
        pet_thor = Pet(nome="Thor", especie="cachorro", idade=7, dono_id=dono_bruno.id)

        db.session.add(pet_rex)
        db.session.add(pet_mimi)
        db.session.add(pet_thor)
        db.session.commit()

    print("Banco criado com sucesso.")
