import streamlit as st
import random

# Lista de muestras
samples = ["Sample 1", "Sample 2", "Sample 3", "Sample 4", "Sample 5",
           "Sample 6", "Sample 7", "Sample 8", "Sample 9", "Sample 10"]

# Inicializar variables de sesión
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'survey_started' not in st.session_state:
    st.session_state.survey_started = False
if 'survey_completed' not in st.session_state:
    st.session_state.survey_completed = False
if 'round_number' not in st.session_state:
    st.session_state.round_number = 1
if 'remaining_samples' not in st.session_state:
    st.session_state.remaining_samples = samples.copy()
if 'selected_samples' not in st.session_state:
    st.session_state.selected_samples = []
if 'rounds_info' not in st.session_state:
    st.session_state.rounds_info = []
if 'participant_name' not in st.session_state:
    st.session_state.participant_name = ""
if 'current_pair' not in st.session_state:
    st.session_state.current_pair = []

# Función para manejar la encuesta
def conduct_survey():
    round_number = st.session_state.round_number

    # Si estamos en una ronda válida
    if round_number <= 9:  
        # Generar un par de muestras si no hay uno para esta ronda
        if not st.session_state.current_pair:
            st.session_state.current_pair = random.sample(st.session_state.remaining_samples, 2)

        st.write(f"Round {round_number}:")
        st.write(f"1: {st.session_state.current_pair[0]}")
        st.write(f"2: {st.session_state.current_pair[1]}")

        # Asignar clave única para cada radio
        choice = st.radio("Select the sample you like more:", 
                          options=['1', '2'], index=0, 
                          key=f"radio_{round_number}")

        # Cuando se presione "Next Round", guardar la selección y avanzar
        if st.button("Next Round", key=f"next_button_{round_number}"):
            if choice == '1':
                selected_sample = st.session_state.current_pair[0]
            else:
                selected_sample = st.session_state.current_pair[1]

            # Guardar el historial de esta ronda
            st.session_state.rounds_info.append({
                'round': round_number,
                'appeared_samples': st.session_state.current_pair,
                'selected_sample': selected_sample
            })

            # Agregar la muestra seleccionada a las muestras seleccionadas
            st.session_state.selected_samples.append(selected_sample)
            st.session_state.remaining_samples.remove(selected_sample)

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

# Panel de administración visible solo si el admin está autenticado y la encuesta aún no comienza
if st.session_state.authenticated and not st.session_state.survey_started:
    st.subheader("Admin Panel")
    st.write("Real-time survey results:")
    for info in st.session_state.rounds_info:
        st.write(f"Participant: {st.session_state.participant_name}, Round {info['round']}: Appeared Samples: {info['appeared_samples']}, Selected Sample: {info['selected_sample']}")

# Mostrar los resultados al final de la encuesta
if st.session_state.survey_completed:
    st.write("Survey completed. Here are your results:")
    for info in st.session_state.rounds_info:
        st.write(f"Round {info['round']}: Appeared Samples: {info['appeared_samples']}, Selected Sample: {info['selected_sample']}")

    if st.button("Finish Survey"):
        st.write("Thank you for participating!")
