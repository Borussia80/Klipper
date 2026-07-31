Rails.application.routes.draw do
  namespace :api, defaults: { format: :json } do
    namespace :v1 do
      get  "health",          to: "health#index"
      post "auth/sign_up",    to: "auth#sign_up"
      post "auth/sign_in",    to: "auth#sign_in"

      post  "password_resets",        to: "password_resets#create"
      patch "password_resets/:token", to: "password_resets#update"

      resources :accounts,      only: %i[index show create update destroy]
      resources :categories,    only: %i[index show create update destroy]
      resources :members,       only: %i[index show create update destroy]
      resources :transactions,  only: %i[index show create update destroy]
      resources :investments,   only: %i[index show create update destroy] do
        collection { get :portfolio }
      end
      resources :budgets,       only: %i[index show create update destroy] do
        collection { get :summary }
      end

      resources :quotes, only: [:index]
      resources :imports, only: [:create] do
        collection do
          post :preview
          post :confirm
        end
      end

      namespace :reports do
        get :monthly
        get :net_worth
        get :net_worth_history
        get :natureza_split
        get :reimbursement_coverage
        get :debt_ranking
      end

      resource :users, only: [] do
        get   :me,       on: :collection
        patch :me,       on: :collection, action: :update
        post  :password, on: :collection
        post  :logout,   on: :collection
      end
    end
  end
end
