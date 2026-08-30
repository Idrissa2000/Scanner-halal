    # ===== MENUS DANS HOME - AVEC VERROU VIP =====
    st.markdown("### 📱 Menus")
    m1, m2, m3 = st.columns(3)
    with m1:
        if st.button("🍎\nAliments 🔒", use_container_width=True):
            if not user.get('is_vip'):
                st.session_state.bottom_nav = "VIP_ALIMENTS"
            else:
                st.session_state.selected_menu = "Aliments"
            st.rerun()
        if st.button("📜\nCoran ✅", use_container_width=True):
            st.session_state.selected_menu = "Coran"
            st.rerun()
    with m2:
        if st.button("📋\nMa Liste", use_container_width=True):
            st.session_state.selected_menu = "Ma Liste"
            st.rerun()
        if st.button("🤲\nDouas 🔒", use_container_width=True):
            if not user.get('is_vip'):
                st.session_state.bottom_nav = "VIP_DOUAS"
            else:
                st.session_state.selected_menu = "Douas"
            st.rerun()
    with m3:
        if st.button("🎮\nJeu", use_container_width=True):
            st.session_state.selected_menu = "Jeu"
            st.rerun()
        if st.button("📚\nHadiths 🔒", use_container_width=True):
            if not user.get('is_vip'):
                st.session_state.bottom_nav = "VIP_HADITHS"
            else:
                st.session_state.selected_menu = "Hadiths"
            st.rerun()
