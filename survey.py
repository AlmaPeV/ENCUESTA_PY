import streamlit as st
import random

# Lista de muestras
samples = ["Sample 1", "Sample 2", "Sample 3", "Sample 4", "Sample 5",
           "Sample 6", "Sample 7", "Sample 8", "Sample 9", "Sample 10"]

# Inicializar variables de sesión
session_vars = {
    'authenticated': False,
    'survey_started': False,
    'survey_completed': False,
    'round_number': 1,
    'remaining_samples': samples.copy(),
    'selected_samples': [],
    'rounds_info': [],
    'participant_name': "",
    'current_sample': None,
    'current_pair': []
}

for var, default in session_vars.items():
    if var not in st.session_state:
        st.session_state[var] = default

# Función para manejar la encuesta
def conduct_survey():
    round_number = st.session_state.round_number

    # Si estamos en una ronda válida
    if round_number <= 9:
        # Generar un par de muestras para cada ronda
        if not st.session_state.current_pair:
            if round_number == 1:
                st.session_state.current_pair = random.sample(st.session_state.remaining_samples, 2)
            else:
                new_sample = random.choice([sample for sample in st.session_state.remaining_samples if sample != st.session_state.current_sample])
                st.session_state.current_pair = [st.session_state.current_sample, new_sample]

        st.write(f"Round {round_number}:")
        st.write(f"1: {st.session_state.current_pair[0]}")
        st.write(f"2: {st.session_state.current_pair[1]}")

        # Asignar clave única para cada radio
        choice = st.radio("Select the sample you like more:", 
                          options=['1', '2'], index=0, 
                          key=f"radio_{round_number}")

        # Cuando se presione "Next Round", guardar la selección y avanzar
        if st.button("Next Round", key=f"next_button_{round_number}"):
            selected_sample = st.session_state.current_pair[int(choice)-1]
            st.session_state.current_sample = selected_sample

            # Guardar el historial de esta ronda
            st.session_state.rounds_info.append({
                'round': round_number,
                'appeared_samples': st.session_state.current_pair,
                'selected_sample': selected_sample
            })

            # Agregar la muestra seleccionada a las muestras seleccionadas y remover la no seleccionada de las restantes
            st.session_state.selected_samples.append(selected_sample)
            remaining_sample = st.session_state.current_pair[1] if selected_sample == st.session_state.current_pair[0] else st.session_state.current_pair[0]
            st.session_state.remaining_samples.remove(remaining_sample)

            # Avanzar a la siguiente ronda
            st.session_state.round_number += 1

            # Limpiar el par actual para generar uno nuevo en el siguiente round
            st.session_state.current_pair = []

            return

    else:
        st.session_state.survey_completed = True

# Inicializar la app de Streamlit
st.title("Sample Preference Survey")

# Sección de autenticación para el panel de administración, SOLO antes de que comience la encuesta
if not st.session_state.survey_started:
    participant_name = st.text_input("Enter your name or code to start the survey:")
    if participant_name and st.button("Start Survey"):
        st.session_state.participant_name = participant_name
        st.session_state.survey_started = True
else:
    # Mostrar la encuesta si ya ha comenzado
    if not st.session_state.survey_completed:
        conduct_survey()

# Sección de administrador (solo visible si no ha comenzado la encuesta y se introduce la contraseña)
if not st.session_state.survey_started:
    password = st.text_input("Enter password to access the admin panel:", type='password')
    if password == '0103':
        st.session_state.authenticated = True
        st.success("Access granted")
    elif password and password != '0103':
        st.error("Invalid password")

# Panel de administración visible solo si el admin está autenticado y la encuesta ha comenzado
if st.session_state.authenticated:
    st.subheader("Admin Panel")
    st.write("Real-time survey results:")
    for info in st.session_state.rounds_info:
        st.write(f"Participant: {st.session_state.participant_name}, Round {info['round']}: Appeared Samples: {info['appeared_samples']}, Selected Sample: {info['selected_sample']}")

    if st.session_state.survey_started and not st.session_state.survey_completed:
        st.subheader("Current Samples for Delivery")
        st.write(f"Current participant: {st.session_state.participant_name}")
        st.write(f"Round {st.session_state.round_number}: Appeared Samples: {st.session_state.current_pair}")

# Mostrar los resultados al final de la encuesta
if st.session_state.survey_completed:
    st.write("Survey completed. Here are your results:")
    for info in st.session_state.rounds_info:
        st.write(f"Round {info['round']}: Appeared Samples: {info['appeared_samples']}, Selected Sample: {info['selected_sample']}")

    if st.button("Finish Survey"):
        st.session_state.update(session_vars)
        st.write("Thank you for participating!")
